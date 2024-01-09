import nidaqmx

class PXI6284Controller:

    """
        This class has been designed for controlling the functions related to pxi6284(analog input device), but you will also find the other 
        functions which can control the analog output devices like pxi6738.

        This class uses the functions already defined in the nidaqmx library. For more information about the original 
        functions described in the library itself, you should check with the documentation of the original function. 
        There, the explaination is in more detail. For doing so, one way is to check the file named pxi6284.py and 
        hover the cursor over the functions which are used inside the functions of the class PXI6284Controller.
    
    
    """

    def __init__(self):
        # Initialize a new NI-DAQmx task
        self.task = nidaqmx.Task()

    def initialize_ai_voltage_channel(self, channel_name):
        '''
            This function initializes an analog input (AI) voltage channel.
            You can use it to set up the channel from which you want to acquire analog voltage data.

            Arguments: 
                
                channel_name (string): Specifies the name of the analog input voltage channel to initialize. You can find out what is the name of your channel in NI MAX software. You can also change the name of your channels. Typical channel name examples =  ('Dev1/ai3' --> means analog input channel 3 of the device 1)
        '''
        self.task.ai_channels.add_ai_voltage_chan(channel_name)



        

    def initialize_ao_voltage_channel(self, channel_name):
        """
            This function initializes an analog output (AO) voltage channel.
            You can use it to set up the channel to which you want to output analog voltage data.

            Arguments: 
                        channel_name (string): Specifies the name of the analog output voltage channel to initialize.
        """
        self.task.ao_channels.add_ao_voltage_chan(channel_name)




    def initialize_di_channel(self, channel_name):
        """
            This function initializes a digital input (DI) channel.
            You can use it to set up the channel from which you want to acquire digital data.
            
            
            Arguments: 
                        channel_name (string): Specifies the name of the digital input channel to initialize.        
        """
        self.task.di_channels.add_di_chan(channel_name)





    def initialize_do_channel(self, channel_name):
        """
            This function initializes a digital output (DO) channel.
            You can use it to set up the channel to which you want to output digital data.
        
            Arguments:
                        channel_name (string): Specifies the name of the digital output voltage channel to initialize.
        """
        self.task.do_channels.add_do_chan(channel_name)





    def start_task(self):
        """
            This function starts the data acquisition or generation task.
            You need to call this function after configuring the channels and timing to begin acquiring or generating data.

        """
        self.task.start()





    def stop_task(self):
        """
            This function stops the data acquisition or generation task.
            You can call this function to stop the task manually.
        """
        self.task.stop()





    def read_data(self, num_samples):
        """
            This function reads acquired data from an analog or digital input channel.
            You need to provide the number of samples to read as num_samples.
            It returns the acquired data as a list or array.
        
            Arguments:
                        num_samples: An integer specifying the number of samples to read from the analog or digital input channel.
        """
        return self.task.read(number_of_samples_per_channel=num_samples)
    




    def write_data(self, data):
        """
            This function writes data to an analog or digital output channel.
            You need to provide the data to be written as data, which should be a list or array.

            Arguments: 
                        data: A list or array containing the data you want to write to the analog or digital output channel.
        """
        self.task.write(data)





    def configure_sample_clock_timing(self, rate, active_edge):
        """
            This function configures the sample clock timing for the task.
            You can set the sampling rate using the rate parameter and choose the active edge of the sample clock using the active_edge parameter.
            This is useful when you want to acquire or generate data at a specific rate.

            Arguments: 
                        rate: A float representing the desired sample clock rate in samples per second.
                        active_edge: A value from the nidaqmx.constants.Edge enumeration indicating the desired active edge of the sample clock.
        """
        self.task.timing.cfg_samp_clk_timing(rate=rate, active_edge=active_edge)





    def configure_implicit_timing(self, sample_mode):
        """
            This function configures implicit timing for digital I/O.
            You need to specify the sample mode (e.g., continuous or finite) to determine how the digital I/O should operate.

            This function sets only the number of samples to acquire or generate without specifying timing. Typically, you should use this 
            instance when the task does not require sample timing, such as tasks that use counters for buffered frequency measurement, 
            buffered period measurement, or pulse train generation. For finite counter output tasks, **samps_per_chan** is the number 
            of pulses to generate.

            Arguments:
                        sample_mode: A value from the nidaqmx.constants.AcquisitionType enumeration specifying the sample mode, such as continuous or finite.
        """
        self.task.timing.cfg_implicit_timing(sample_mode)





    def set_sample_clock_rate(self, rate):
        """
            This function sets the sample clock rate.
            You can use it to change the sample clock rate after configuring the sample clock timing.

            Arguments:
                        rate: A float representing the desired sample clock rate in samples per second.
        """
        self.task.timing.samp_clk_rate = rate





    def set_sample_clock_active_edge(self, edge):
        """
            This function sets the active edge of the sample clock.
            You can use it to change the active edge after configuring the sample clock timing.
        
            Arguments:
                        edge: A value from the nidaqmx.constants.Edge enumeration indicating the desired active edge of the sample clock.
        """
        self.task.timing.samp_clk_active_edge = edge





    def set_sample_timing_type(self, timing_type):
        """
            This function sets the sample timing type.
            You can specify the 'timing_type' (e.g., samples or time) to determine how the sample timing should be interpreted.
        
            Arguments:
                        timing_type: A value from the nidaqmx.constants.SampleTimingType enumeration specifying the sample timing type, such as samples or time.
        """
        self.task.timing.samp_timing_type = timing_type





    def configure_digital_edge_start_trigger(self, trigger_source, edge):
        """
            This function configures a digital edge start trigger for the task.
            You need to provide the 'trigger_source' (e.g., a digital input channel) and the 'edge' (e.g., rising or falling) to specify the trigger conditions.
        
            Arguments:
                        trigger_source: A string representing the name of the trigger source, which could be a digital input channel.
                        edge: A value from the nidaqmx.constants.Edge enumeration indicating the trigger condition (rising or falling edge).
        """
        self.task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source, edge)





    def configure_analog_edge_start_trigger(self, trigger_source, edge, level):
        """
            This function configures an analog edge start trigger for the task.
            You need to provide the trigger_source (e.g., an analog input channel), the edge (e.g., rising or falling), and the level (e.g., voltage threshold) to specify the trigger conditions.
        
            Arguments:
                        trigger_source: A string representing the name of the trigger source, which could be an analog input channel.
                        edge: A value from the nidaqmx.constants.Edge enumeration indicating the trigger condition (rising or falling edge).
                        level: A float specifying the voltage threshold for the trigger.
        """
        self.task.triggers.start_trigger.cfg_anlg_edge_start_trig(trigger_source, edge, level)





    def configure_digital_pattern_start_trigger(self, trigger_source, pattern, condition):
        """
            This function configures a digital pattern start trigger for the task.
            You need to provide the 'trigger_source' (e.g., a digital input channel), the 'pattern' (e.g., bit pattern to match), and the 'condition' (e.g., match on equality or inequality) to specify the trigger conditions.
        
            Arguments:
                        trigger_source: A string representing the name of the trigger source, which could be a digital input channel.
                        pattern: An integer specifying the bit pattern to match for the trigger condition.
                        condition: A value from the nidaqmx.constants.TriggerType enumeration indicating the trigger condition (e.g., match on equality or inequality).
        """
        self.task.triggers.start_trigger.cfg_dig_pattern_start_trig(trigger_source, pattern, condition)





    def configure_no_start_trigger(self):
        """
            This function configures no start trigger for the task.
            You can use it when you don't need any trigger conditions to start the task.
        """
        self.task.triggers.start_trigger.cfg_none_start_trig()





    def __del__(self):
        """
            It is a special method in Python classes that is automatically called when an object is about to be destroyed and garbage collected. In the context of the PXI6284Controller class, the __del__ method is used to clean up and release system resources associated with the NI-DAQmx task.
        
        """
        self.task.close()





# controller = PXI6284Controller()
# controller.initialize_ai_voltage_channel("Dev1/ai5")
# controller.start_task()
# data = controller.read_data(100)
# controller.stop_task()
# print(data)

# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation

# controller = PXI6284Controller()
# controller.initialize_ai_voltage_channel("Dev1/ai5")
# controller.start_task()

# # Set up the figure and axes
# fig, ax = plt.subplots()
# line, = ax.plot([], [])

# # Initialize empty lists to store x and y data
# x_data, y_data = [], []

# # # Define the update function for the animation
# # def update(frame):
# #     # Read a chunk of data
# #     data = controller.read_data(100)

# #     # Update the x and y data lists
# #     x_data.extend(range(len(data)))
# #     y_data.extend(data)

# #     # Update the line data
# #     line.set_data(x_data, y_data)

# #     # Recalculate the data limits and autoscale the plot
# #     ax.relim()
# #     ax.autoscale_view()

# #     return line,

# def update(frame):
#     # Check if the task has completed
#     if not controller.is_task_done():
#         # Read a chunk of data
#         data = controller.read_data(100)
        
#         # Update the x and y data lists
#         x_data.extend(range(len(x_data), len(x_data) + len(data)))
#         y_data.extend(data)
        
#         # Update the line data
#         line.set_data(x_data, y_data)
        
#         # Adjust the x-axis limits based on the new data
#         ax.set_xlim(min(x_data), max(x_data))
        
#         # Adjust the y-axis limits based on the new data
#         min_y = min(y_data)
#         max_y = max(y_data)
#         ax.set_ylim(min_y - (max_y - min_y) * 0.1, max_y + (max_y - min_y) * 0.1)
    
#     return line,


# # Create the animation
# ani = FuncAnimation(fig, update, frames=None, blit=True, interval=100, cache_frame_data=False)

# # Show the plot
# plt.show()

# # Stop the task after the plot is closed
# controller.stop_task()

desired_num_data_points = 1000

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

controller = PXI6284Controller()
controller.initialize_ai_voltage_channel("Dev1/ai5")
controller.start_task()

# Set up the figure and axes
fig, ax = plt.subplots()
line, = ax.plot([], [])

# Initialize empty lists to store x and y data
x_data, y_data = [], []

# Define the update function for the animation
def update(frame):

    data = controller.read_data(10)
    
    x_data.extend(range(len(x_data), len(x_data) + len(data)))
    y_data.extend(data)
    
    line.set_data(x_data, y_data)
    
    ax.set_xlim(min(x_data), max(x_data))
    
    min_y = min(y_data)
    max_y = max(y_data)
    ax.set_ylim(min_y - (max_y - min_y) * 0.1, max_y + (max_y - min_y) * 0.1)

    if len(x_data) >= desired_num_data_points:
        controller.stop_task()
        ani.event_source.stop()
    
    return line,

# Create the animation
ani = FuncAnimation(fig, update, frames=None, blit=True, interval=100, cache_frame_data=False)

# Show the plot
plt.show()


