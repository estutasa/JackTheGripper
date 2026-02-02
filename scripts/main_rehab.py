#!/usr/bin/python3
"""
FILE: main_rehab.py
PURPOSE: Main part. Initiliazes the hardware interface, the 3D visualiztation, rehabilitation logic, and manages
user commands via a console-based loop
"""
import logging
import sys
import os
import threading
import time

# path fix for SCN library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication
from scn.hwi.hwi import HardwareInterface as Hwi
from scn.ctrl.handler import LedControl, UdrControl, CfControl, IdControl, SensControl, EventsControl
from scn.sc.data_publisher import DataPublisher
from led_feedback import LedFeedbackRehab
from visualizator_3d import Visualizator3D

def console_loop(rehab_sys, hwi, data_pub, handlers):
    """
    Handles real-time user input from the terminal to control the system
    Inputs: rehab_sys. hwi, data_pub and handlers
    Outputs:none
    """
    print(">>> JACK THE GRIPPER: READY <<<")
    print("Sequence: c -> udr 63 -> store offsets -> start")
    print("To terminate the experiment, please enter: stop -> d -> q")
    while True:
        try:
            cmd = input().strip()
            if not cmd: continue
            if cmd == "q": 
                print("Exiting...")
                rehab_sys.stop()
                hwi.close()     
                os._exit(0)  
            if cmd == "d":
                rehab_sys.stop()
                hwi.disconnect()
                continue
            if cmd == "c":
                data_pub.reset()
                hwi.connect()
                continue
            if cmd == "start":
                rehab_sys.start()
                continue
            if cmd == "stop":
                rehab_sys.stop()
                continue

            #Command handler (handles 'store offsets', 'udr 63', etc.)
            handled = False
            for h in handlers:
                if h.handleCommand(cmd):
                    handled = True
                    break

            if not handled:
                print(f"Unknown command: {cmd}")
        except KeyboardInterrupt:
            rehab_sys.stop()
            hwi.close()
            os._exit(0)

if __name__ == '__main__':
       
    logging.basicConfig(level=logging.CRITICAL)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_stl = os.path.join(base_dir, 'models', 'cylinder_5cm.STL')
    
    app = QApplication(sys.argv)
    viz = Visualizator3D(file_stl)
    viz.show()

    hwi = Hwi(Hwi.DefaultConfig())
    hwi.open()
    hwi.ctrl().reader().start()
    hwi.data().reader().start()

    data_pub = DataPublisher(hwi)
    led_ctrl = LedControl(hwi)
    handlers = [IdControl(hwi), SensControl(hwi), CfControl(hwi), 
                UdrControl(hwi), led_ctrl, EventsControl(hwi)]

    rehab_sys = LedFeedbackRehab(hwi, data_pub, led_ctrl, visualizer=viz)

    threading.Thread(target=console_loop, args=(rehab_sys, hwi, data_pub, handlers), daemon=True).start()

    sys.exit(app.exec())
