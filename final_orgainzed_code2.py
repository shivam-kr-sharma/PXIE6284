# This code provides a userinterface for entering the values or arguments and then it saves the data in the format which you will prefer. It will also offer you live plotting of the data.



from tkinter import filedialog
import os
import tkinter as tk
from tkinter import simpledialog
import nidaqmx
import time
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class DataAcquisitionAndPlotting:
    def __init__(self):
        self.sample_rate = 0
        self.duration = 0.0
        self.duration_unit = 'seconds'  # Initialize duration_unit to 'seconds' by default
        self.num_samples = 0
        self.csv_file_path = ""
        self.selected_channels = []
        self.data_ready_event = threading.Event()
        self.plotting_active = True  # Flag to control live plotting

    def is_positive_integer(self, value):
        try:
            int_value = int(value)
            if int_value >= 0:
                return True
        except ValueError:
            pass
        return False

    def is_non_negative_float(self, value):
        try:
            float_value = float(value)
            if float_value >= 0.0:
                return True
        except ValueError:
            pass
        return False

    def create_channel_selection_dialog(self):
        root = tk.Tk()
        root.withdraw()

        num_channels = 32

        # Function to update the channels list when a checkbox is clicked
        def update_channels(channel_var, channel_num):
            if channel_var.get():
                self.selected_channels.append(f"Dev1/ai{channel_num}")
            else:
                self.selected_channels.remove(f"Dev1/ai{channel_num}")

        # Create the dialog box
        dialog = tk.Toplevel(root)
        dialog.title("Data Acquisition Configuration")

        # Create and add checkboxes for each channel
        channel_frame = tk.Frame(dialog)
        channel_frame.pack(padx=10, pady=5)
        for i in range(num_channels):
            channel_var = tk.BooleanVar()
            channel_var.set(False)
            channel_num = i
            checkbox = tk.Checkbutton(channel_frame, text=f"Channel {channel_num}", variable=channel_var, command=lambda var=channel_var, num=channel_num: update_channels(var, num))
            checkbox.pack(anchor='w')

        # --- Add sections for other input parameters ---
        param_frame = tk.Frame(dialog)
        param_frame.pack(padx=10, pady=5)

        # Sample Rate section
        sample_rate_label = tk.Label(param_frame, text="Sample Rate ( in samples per second):")
        sample_rate_label.grid(row=0, column=0, padx=5, pady=5)
        sample_rate_entry = tk.Entry(param_frame)
        sample_rate_entry.grid(row=0, column=1, padx=5, pady=5)

        # Duration section
        duration_label = tk.Label(param_frame, text="Duration:")
        duration_label.grid(row=1, column=0, padx=5, pady=5)
        duration_entry = tk.Entry(param_frame)
        duration_entry.grid(row=1, column=1, padx=5, pady=5)
        duration_unit_var = tk.StringVar(value="seconds")
        duration_unit_options = ["seconds", "minutes", "hours"]
        duration_unit_menu = tk.OptionMenu(param_frame, duration_unit_var, *duration_unit_options)
        duration_unit_menu.grid(row=1, column=2, padx=5, pady=5)

        # Num Samples section
        num_samples_label = tk.Label(param_frame, text="Num Samples (read in each batch):")
        num_samples_label.grid(row=2, column=0, padx=5, pady=5)
        num_samples_entry = tk.Entry(param_frame)
        num_samples_entry.grid(row=2, column=1, padx=5, pady=5)

        # CSV File Path section
        csv_file_path_label = tk.Label(param_frame, text="File Path:")
        csv_file_path_label.grid(row=3, column=0, padx=5, pady=5)

        def browse_csv_file():
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
            if file_path:
                csv_file_path_var.set(file_path)

        csv_file_path_var = tk.StringVar()
        csv_file_path_entry = tk.Entry(param_frame, textvariable=csv_file_path_var)
        csv_file_path_entry.grid(row=3, column=1, padx=5, pady=5)

        # Button to open file explorer
        browse_button = tk.Button(param_frame, text="Browse", command=browse_csv_file)
        browse_button.grid(row=3, column=2, padx=5, pady=5)

        # Label to display the selected file path
        selected_file_label = tk.Label(param_frame, text="", wraplength=300)  # Adjust the wraplength as needed
        selected_file_label.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        def update_selected_file_label(*args):
            file_path = csv_file_path_var.get()
            if os.path.exists(file_path):
                selected_file_label.config(text=file_path)
            else:
                selected_file_label.config(text="File path not found")

        # Add a trace to update the label when the content of csv_file_path_var changes
        csv_file_path_var.trace_add('write', update_selected_file_label)

        def on_okay():
            # Get the input values from the entry fields
            sample_rate_value = sample_rate_entry.get()
            duration_value = duration_entry.get()
            duration_unit_value = duration_unit_var.get()  # Get the selected duration unit
            num_samples_value = num_samples_entry.get()
            csv_file_path_value = csv_file_path_entry.get()

            # Validate the input for sample_rate, duration, num_samples
            if not self.is_positive_integer(sample_rate_value) or int(sample_rate_value) <= 0:
                sample_rate_entry.delete(0, tk.END)
                sample_rate_entry.insert(0, "Invalid sample rate")
                return

            if not self.is_non_negative_float(duration_value):
                duration_entry.delete(0, tk.END)
                duration_entry.insert(0, "Invalid duration")
                return

            if not self.is_positive_integer(num_samples_value) or int(num_samples_value) <= 0:
                num_samples_entry.delete(0, tk.END)
                num_samples_entry.insert(0, "Invalid num samples")
                return

            # Convert the validated values to appropriate data types
            self.sample_rate = int(sample_rate_value)
            self.duration = float(duration_value)
            self.num_samples = int(num_samples_value)
            self.csv_file_path = csv_file_path_value

            # Set the duration_unit based on the selected option
            self.duration_unit = duration_unit_value

            # All entries are valid, destroy the dialog
            dialog.destroy()

        # Add the "OK" button
        ok_button = tk.Button(dialog, text="OK", command=on_okay)
        ok_button.pack(pady=10)

        # Run the dialog box
        dialog.wait_window()

    def acquire_and_save_data(self):
        # Convert the duration to seconds based on the user-specified unit
        duration_in_seconds = self.duration
        if self.duration_unit == 'minutes':
            duration_in_seconds *= 60
        elif self.duration_unit == 'hours':
            duration_in_seconds *= 3600

        # Prepare the column headings based on the channel names
        column_headings = [self.selected_channels[i] for i in range(len(self.selected_channels))]

        with nidaqmx.Task() as task:
            for channel in self.selected_channels:
                task.ai_channels.add_ai_voltage_chan(channel)

            task.timing.cfg_samp_clk_timing(rate=self.sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=self.num_samples)

            # Write the header to the CSV file only once
            pd.DataFrame(columns=column_headings).to_csv(self.csv_file_path, index=False)

            # Set the data_ready_event to indicate that data is ready for plotting
            self.data_ready_event.set()

            start_time = time.time()
            while (time.time() - start_time) < duration_in_seconds:
                data = task.read(number_of_samples_per_channel=self.num_samples)      # read function also takes the argument timeout- which means how much time the read function can wait before declaring timeout, to read the batch of data.

                if len(self.selected_channels) == 1:
                    data_dict = {self.selected_channels[0]: data}  # Single channel data is a 1D array
                else:
                    data_dict = {self.selected_channels[i]: data[i] for i in range(len(self.selected_channels))}

                # Append data to the CSV file
                pd.DataFrame(data_dict, columns=column_headings).to_csv(self.csv_file_path, mode='a', index=False, header=False)
        # Set the plotting_active flag to False after the duration is over
        self.plotting_active = False

    def live_plot_from_csv(self):
        plt.style.use('fivethirtyeight')  # Set the style for the current function

        # Number of data points to display on the x-axis
        x_range = 1500

        def animate(i):
            if not self.plotting_active:
                # If plotting is not active, stop updating the plot
                ani.event_source.stop()
                return

            data = pd.read_csv(self.csv_file_path)

            # Limit the number of data points displayed on the x-axis
            num_data_points = len(data)
            start_idx = max(num_data_points - x_range, 0)
            end_idx = num_data_points
            x = np.arange(start_idx, end_idx)

            plt.cla()
            for channel in data.columns:
                y = data[channel][start_idx:end_idx]
                plt.plot(x, y, label=channel, linewidth=1)
                plt.ylim(-5, 5)

            plt.legend(loc='upper left')
            plt.tight_layout()

        # Wait until data is ready for plotting
        self.data_ready_event.wait()
        
        ani = FuncAnimation(plt.gcf(), animate, interval=100)

        plt.tight_layout()
        plt.show()

    def run(self):
        self.create_channel_selection_dialog()

        # Create threads with function references as targets
        acquire_thread = threading.Thread(
            target=self.acquire_and_save_data
        )

        plot_thread = threading.Thread(
            target=self.live_plot_from_csv
        )

        # Start the threads
        acquire_thread.start()
        plot_thread.start()

        # while True:
        #     # If the plot window is closed, set the plotting_active flag to False and exit the loop
        #     if not plt.fignum_exists(1):
        #         self.plotting_active = False
        #         break
            # time.sleep(0.1)  # Adjust the sleep time as needed

        # Wait for the threads to complete (optional, only if needed)
        acquire_thread.join()
        plot_thread.join()

if __name__ == "__main__":
    data_acquisition_and_plotting = DataAcquisitionAndPlotting()
    data_acquisition_and_plotting.run()
