#
# -*- coding: utf-8  -*-
#=================================================================
# Created by: Jieming Ye
# Created on: Feb 2024
# Last Modified: Feb 2024
#=================================================================
# Copyright (c) 2024 [Jieming Ye]
#
# This Python source code is licensed under the 
# Open Source Non-Commercial License (OSNCL) v1.0
# See LICENSE for details.
#=================================================================
"""
Pre-requisite: 
base_frame.py
Used Input:
N/A
Expected Output:
Detailed windows based on user selection
Description:
This script defines individual checking option in a new ‘class’ object following logic stated in section 4.1.

"""
#=================================================================
# VERSION CONTROL
# V1.0 (Jieming Ye) - Initial Version
#=================================================================
# Set Information Variable
# N/A
#=================================================================


import tkinter as tk
import threading
from multiprocessing import Process

from vision_oslo_extension.shared_contents import SharedVariables, Local_Shared, SharedMethods
from vision_oslo_extension.base_frame import BasePage
from vision_oslo_extension import model_check

# Basic Information Summary
class C01(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 1: Basic Information Summary',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce various summary reports inlcuding branch list, supply point list, transformer list and errors or warnings summary. This process should be fairly quick.',aspect = 1200, font = controller.text_font)
        explain.pack()

        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_model_check(),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Check", command=lambda: controller.show_frame("PageTwo"))
        button2.grid(row = 0, column = 1)

    def run_model_check(self):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            time_start = Local_Shared.time_start
            time_end = Local_Shared.time_end
            option_select = "1"
            text_input = Local_Shared.text_input
            low_v = Local_Shared.low_threshold
            high_v = Local_Shared.high_threshold
            time_step = Local_Shared.time_step

            # Run the batch processing function in a separate thread
            thread = threading.Thread(target=SharedMethods.launch_new_thread_or_process, 
                                      args=("model_check.py",sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            thread.start()
        
        except Exception as e:
            SharedMethods.print_message(f"ERROR: Error in threading...{e} \nContact Support / Do not carry out multiple tasking at the same time. ", '31')

# Connectivity
class C02(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 2: Connectivity Report',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce two summaries. One showing the node connection summary. One showing all connected nodes from the supply points.',aspect = 1200, font = controller.text_font)
        explain.pack()

        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_model_check(),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Check", command=lambda: controller.show_frame("PageTwo"))
        button2.grid(row = 0, column = 1)


    def run_model_check(self):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            time_start = Local_Shared.time_start
            time_end = Local_Shared.time_end
            option_select = "2"
            text_input = Local_Shared.text_input
            low_v = Local_Shared.low_threshold
            high_v = Local_Shared.high_threshold
            time_step = Local_Shared.time_step

            # Run the batch processing function in a separate thread
            thread = threading.Thread(target=SharedMethods.launch_new_thread_or_process, 
                                      args=("model_check.py",sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            thread.start()
        
        except Exception as e:
            SharedMethods.print_message(f"ERROR: Error in threading...{e} \nContact Support / Do not carry out multiple tasking at the same time. ", '31')

# Plotting
class C03(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 3: Network Connection Plot',font = controller.sub_title_font)
        head.pack()

        explain = tk.Label(master=self.headframe, text = 'This will create a plot (A3 Picture format) of the OSLO network.', font = controller.text_font)
        explain.pack()

        explain1 = tk.Label(master=self.headframe, text = 'NOTE: AC Network Plot is Regulated (Option 1 and 2).', font = controller.text_font)
        explain1.pack()

        explain3 = tk.Label(master=self.headframe, text = 'NOTE: DC Network Plot is Random (Option 3). Different plots each run.', font = controller.text_font)
        explain3.pack()
        
        explain2 = tk.Label(master=self.headframe, text = 'WARNING: This process will freeze this window once RUN due to Plotting Function Limitation.', font = controller.text_font)
        explain2.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: AC OSLO Network Plotting (NOT show Branch ID)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: AC OSLO Network Plotting (Show Branch ID)',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: DC OSLO Network Plotting (Random Gen, To Be Improved)', value="3", variable=option1)
        choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        # choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: TO BE DECIDED', value="4", variable=option1)
        # choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_model_check(option1),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Check", command=lambda: controller.show_frame("PageTwo"))
        button2.grid(row = 0, column = 1)


    def run_model_check(self, option1):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            time_start = Local_Shared.time_start
            time_end = Local_Shared.time_end
            option_select = "3"
            text_input = option1.get()
            low_v = Local_Shared.low_threshold
            high_v = Local_Shared.high_threshold
            time_step = Local_Shared.time_step

            # Run the batch processing function in a separate thread
            process = Process(target=SharedMethods.launch_new_thread_or_process, 
                                      args=("model_check.py",sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            process.start()
        
        except Exception as e:
            SharedMethods.print_message(f"ERROR: Error in multiprocessing...{e} \nContact Support / Do not carry out multiple tasking at the same time. ", '31')


# Batch Simulation Running Control
class C04(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 4: Batch Simulation Running',font = controller.sub_title_font)
        head.pack()

        explain = tk.Label(master=self.headframe, text = 'This support automatically running of multiple simulations.', font = controller.text_font)
        explain.pack()

        explain1 = tk.Message(master=self.headframe, text = 'Note that this supports from VISION RN-28 onwards. Once the process started, user could stop the process by shutting down the VISION model directly.',aspect = 1200, font = controller.text_font)
        explain1.pack()

        explain2 = tk.Label(master=self.headframe, text = 'NOTE: Import "BatchControlTemplate.csv" to start.', font = controller.text_font)
        explain2.pack()
        
        explain3 = tk.Label(master=self.headframe, text = 'WARNING: This process takes time and the extension tool cannot be used for other purpose once running.', font = controller.text_font)
        explain3.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Only ONE option available for this version.', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        label01 = tk.Label(master=self.inputframe, text = 'Excel Name:',font = controller.text_font)
        label01.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry01 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry01.grid(row = 0,column = 1)

        button_select = tk.Button(master=self.inputframe, text="Select", command = lambda: self.auto_excel_select(input3),width = 10, height =1)
        button_select.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_batch_control(option1,input3),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Check", command=lambda: controller.show_frame("PageTwo"))
        button2.grid(row = 0, column = 1)


    def run_batch_control(self, option1,input3):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            time_start = Local_Shared.time_start
            time_end = Local_Shared.time_end
            option_select = option1.get()
            text_input = input3.get()
            low_v = Local_Shared.low_threshold
            high_v = Local_Shared.high_threshold
            time_step = Local_Shared.time_step

            # Run the batch processing function in a separate process
            process = Process(target=SharedMethods.launch_new_thread_or_process,
                              args=("simulation_batch_run.py",sim_name, main_option, time_start, time_end, option_select,
                                    text_input, low_v, high_v, time_step,SharedVariables.current_path))
            process.start()
        
        except Exception as e:
            SharedMethods.print_message(f"ERROR: Error in multiprocessing...{e} \nContact Support / Do not carry out multiple tasking at the same time. ", '31')