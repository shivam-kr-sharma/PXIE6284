import tkinter as tk
from tkinter import simpledialog
import nidaqmx
import pandas as pd
import time
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

sample_rate = 0
duration = 0.0
num_samples = 0
csv_file_path = ""

def is_positive_integer(value):
    try:
        int_value = int(value)
        if int_value >= 0:
            return True
    except ValueError:
        pass
    return False

def is_non_negative_float(value):
    try:
        float_value = float(value)
        if float_value >= 0.0:
            return True
    except ValueError:
        pass
    return False

def create_channel_selection_dialog():
    root = tk.Tk()
    root.withdraw()

    num_channels = 32
    channels = []  # Initialize the list to store selected channels
    data_ready_event = threading.Event()
    # Function to update the channels list when a checkbox is clicked
    def update_channels(channel_var, channel_num):
        if channel_var.get():
            channels.append(f"Dev1/ai{channel_num}")
        else:
            channels.remove(f"Dev1/ai{channel_num}")

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
    sample_rate_label = tk.Label(param_frame, text="Sample Rate:")
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
    num_samples_label = tk.Label(param_frame, text="Num Samples:")
    num_samples_label.grid(row=2, column=0, padx=5, pady=5)
    num_samples_entry = tk.Entry(param_frame)
    num_samples_entry.grid(row=2, column=1, padx=5, pady=5)

    # CSV File Path section
    csv_file_path_label = tk.Label(param_frame, text="CSV File Path:")
    csv_file_path_label.grid(row=3, column=0, padx=5, pady=5)
    csv_file_path_entry = tk.Entry(param_frame)
    csv_file_path_entry.grid(row=3, column=1, padx=5, pady=5)

    def on_okay():
        global sample_rate, duration, num_samples, csv_file_path

        # Get the input values from the entry fields
        sample_rate_value = sample_rate_entry.get()
        duration_value = duration_entry.get()
        num_samples_value = num_samples_entry.get()
        csv_file_path_value = csv_file_path_entry.get()

        # Validate the input for sample_rate, duration, num_samples
        if not is_positive_integer(sample_rate_value) or int(sample_rate_value) <= 0:
            sample_rate_entry.delete(0, tk.END)
            sample_rate_entry.insert(0, "Invalid sample rate")
            return

        if not is_non_negative_float(duration_value):
            duration_entry.delete(0, tk.END)
            duration_entry.insert(0, "Invalid duration")
            return

        if not is_positive_integer(num_samples_value) or int(num_samples_value) <= 0:
            num_samples_entry.delete(0, tk.END)
            num_samples_entry.insert(0, "Invalid num samples")
            return

        # Convert the validated values to appropriate data types
        sample_rate = int(sample_rate_value)
        duration = float(duration_value)
        num_samples = int(num_samples_value)
        csv_file_path = csv_file_path_value

        # All entries are valid, destroy the dialog
        dialog.destroy()
        data_ready_event.set()  # Set the event to indicate data is ready for plotting



    # Add the "OK" button
    ok_button = tk.Button(dialog, text="OK", command=on_okay)
    ok_button.pack(pady=10)

    # Run the dialog box
    dialog.wait_window()

    return channels, int(sample_rate), float(duration), duration_unit_var.get(), int(num_samples), csv_file_path, data_ready_event

if __name__ == "__main__":
    selected_channels, sample_rate, duration, duration_unit, num_samples, csv_file_path, data_ready_event = create_channel_selection_dialog()
    print("Selected Channels:", selected_channels)
    print("Sample Rate:", sample_rate)
    print("Duration:", duration, duration_unit)
    print("Num Samples:", num_samples)
    print("CSV File Path:", csv_file_path)





def acquire_and_save_data(channels, sample_rate, duration, duration_unit, num_samples, csv_file_path):
    # Convert the duration to seconds based on the user-specified unit
    duration_in_seconds = duration
    if duration_unit == 'minutes':
        duration_in_seconds *= 60
    elif duration_unit == 'hours':
        duration_in_seconds *= 3600

    # Prepare the column headings based on the channel names
    column_headings = [channels[i] for i in range(len(channels))]

    with nidaqmx.Task() as task:
        for channel in channels:
            task.ai_channels.add_ai_voltage_chan(channel)

        task.timing.cfg_samp_clk_timing(rate=sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=num_samples)

        # Write the header to the CSV file only once
        pd.DataFrame(columns=column_headings).to_csv(csv_file_path, index=False)

        start_time = time.time()
        while (time.time() - start_time) < duration_in_seconds:
            data = task.read(number_of_samples_per_channel=num_samples)      # read function also takes the argument timeout- which means how much time the read function can wait before declaring timeout, to read the batch of data.

            if len(channels) == 1:
                data_dict = {channels[0]: data}  # Single channel data is a 1D array
            else:
                data_dict = {channels[i]: data[i] for i in range(len(channels))}

            # Append data to the CSV file
            pd.DataFrame(data_dict, columns=column_headings).to_csv(csv_file_path, mode='a', index=False, header=False)

            # Set the data_ready_event to indicate that data is ready for plotting
            data_ready_event.set()

def live_plot_from_csv(csv_file_path, data_ready_event):
    plt.style.use('fivethirtyeight')  # Set the style for the current function

    # Number of data points to display on the x-axis
    x_range = 10000
    data_ready_event.wait()  # Wait for data to be ready

    def animate(i):
        data = pd.read_csv(csv_file_path)

        # Limit the number of data points displayed on the x-axis
        num_data_points = len(data)
        start_idx = max(num_data_points - x_range, 0)
        end_idx = num_data_points
        x = np.arange(start_idx, end_idx)

        plt.cla()
        for channel in data.columns:
            y = data[channel][start_idx:end_idx]
            plt.plot(x, y, label=channel, linewidth=1)
            # plt.ylim(-20, 20)


        plt.legend(loc='upper left')
        plt.tight_layout()

    ani = FuncAnimation(plt.gcf(), animate, interval=100)

    plt.tight_layout()
    plt.show()


# Create threads with function references as targets
acquire_thread = threading.Thread(
    target=acquire_and_save_data,
    args=(selected_channels, sample_rate, duration, duration_unit, num_samples, csv_file_path)
)

plot_thread = threading.Thread(
    target=live_plot_from_csv,
    args=(csv_file_path, data_ready_event)
)

# Start the threads
acquire_thread.start()
plot_thread.start()

# Wait for the threads to complete (optional, only if needed)
acquire_thread.join()
plot_thread.join()
