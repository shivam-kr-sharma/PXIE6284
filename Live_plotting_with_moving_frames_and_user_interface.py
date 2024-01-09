
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

def create_channel_selection_dialog():
    root = tk.Tk()
    root.withdraw()

    num_channels = 32
    channels = []  # Initialize the list to store selected channels

    # Function to update the channels list when a checkbox is clicked
    def update_channels(channel_var, channel_num):
        if channel_var.get():
            channels.append(f"Dev1/ai{channel_num}")
        else:
            channels.remove(f"Dev1/ai{channel_num}")

    # Create the dialog box
    dialog = tk.Toplevel(root)
    dialog.title("Channel Selection")

    # Create and add checkboxes for each channel
    checkboxes = []
    for i in range(num_channels):
        channel_var = tk.BooleanVar()
        channel_var.set(False)
        channel_num = i
        checkbox = tk.Checkbutton(dialog, text=f"Channel {channel_num}", variable=channel_var, command=lambda var=channel_var, num=channel_num: update_channels(var, num))
        checkbox.pack(anchor='w')
        checkboxes.append(checkbox)

    # Function to handle the "OK" button click
    def on_okay():
        dialog.destroy()

    # Add the "OK" button
    ok_button = tk.Button(dialog, text="OK", command=on_okay)
    ok_button.pack()

    # Run the dialog box
    dialog.wait_window()

    return channels

if __name__ == "__main__":
    selected_channels = create_channel_selection_dialog()
    print("Selected Channels:", selected_channels)

    # Create an empty CSV file with the required column headings
    column_headings = [selected_channels[i] for i in range(len(selected_channels))]
    pd.DataFrame(columns=column_headings).to_csv("acquired_data.csv", index=False)





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

            # Wait for a short period before acquiring data again (adjust as needed)
            # time.sleep(1)

def live_plot_from_csv(csv_file_path):
    plt.style.use('fivethirtyeight')  # Set the style for the current function

    # Number of data points to display on the x-axis
    x_range = 10000
    
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
    args=(selected_channels, 1000, 5, "seconds", 1000, "acquired_data.csv")
)

plot_thread = threading.Thread(
    target=live_plot_from_csv,
    args=("acquired_data.csv",)
)

# Start the threads
acquire_thread.start()
plot_thread.start()

# Wait for the threads to complete (optional, only if needed)
acquire_thread.join()
plot_thread.join()
