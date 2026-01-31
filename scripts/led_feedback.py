""" 
FILE: led_feedback.py
Purpose: Manages real time feedback loop for the rehabilitation systems. 
Coordinates LED colors based on pressure levels and synchronizes 
data tranmission to the 3D visualization interface.
"""
import threading
import time
from scn.ctrl.handler.led_control import COLOR_VAL_MAP
from scn.sc.pkt.data import data_tuple_to_data1200
from event_detection import GripLogic
from ui_bridge import UIBridge

class LedFeedbackRehab:
    def __init__(self, hwi, data_pub, led_ctrl, visualizer=None):
        """
        Initializes feedback controller
        Inputs: hwi, data_pub, led_ctrl, visualizer
        Outputs:none
        """
        self.__hwi = hwi
        self.__data_pub = data_pub
        self.__led_ctrl = led_ctrl
        self.logic = GripLogic()
        self.bridge=None
        if visualizer:
            self.bridge=UIBridge(visualizer)
        self.__started = False
        self.__thread = None
        self.__stop_event = threading.Event()
        self.__mutex = threading.Lock()
        self.__current_color = COLOR_VAL_MAP.get("white")

    def start(self):
        #Starts the background feedback loop thread.
        #Inputs: none
        #Outputs:none
        if not self.__started:
            self.__stop_event.clear()
            self.__thread = threading.Thread(target=self.__run)
            self.__thread.start()
            self.__started = True

    def stop(self):
        """
        Safely stops the background thread and resets the led hardware
        Inputs: none
        Outputs:none
        """
        if self.__started:
            self.__stop_event.set()
            if self.__thread.is_alive():
                self.__thread.join()
            self.__started = False
            self.__led_ctrl.set_led_color_val(COLOR_VAL_MAP.get("white"))
    
    """
    Returns the current execution status of the controller
    Inputs: none
    Outputs:bool, true if loop running
    """
    def isStarted(self): return self.__started

    def __update(self):
        """
        Performs single update cycle, fetches the data, updates UI and sets LED state
        Inputs:none
        Outputs:none
        """
        sc_data_list = self.__data_pub.sc_data()
        if not sc_data_list: return

        raw_data_dict = {}
        max_f = 0.0
        
        for sc_data in sc_data_list:
            cell_id = sc_data[0] 
            d = data_tuple_to_data1200(sc_data)
            f_val_cell = max(d.get("force", [0.0]))
            if 1 <= cell_id <= 16:
                raw_data_dict[cell_id] = {"force": f_val_cell}
            
            if f_val_cell > max_f: 
                max_f = f_val_cell

        if self.bridge:
            self.bridge.process_and_stream(raw_data_dict)

        state = self.logic.classify(max_f)
        
        with self.__mutex:
            if state == 1: 
                self.__current_color = COLOR_VAL_MAP.get("green")
            elif state == 2: 
                self.__current_color = COLOR_VAL_MAP.get("red")
            else: 
                self.__current_color = COLOR_VAL_MAP.get("white")

                
    def __run(self):
        """
        Main loop execution for the background thread
        Inputs: none
        Outputs:none
        """
        while not self.__stop_event.is_set():
            self.__update()
            with self.__mutex:
                color = self.__current_color
            self.__led_ctrl.set_led_color_val(color)
            time.sleep(0.04) # 25 Hz update rate