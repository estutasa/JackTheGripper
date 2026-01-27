"""
FILE HEADER: main_rehab.py
PURPOSE: Main entry point for the Stroke Rehab Handle with CLI support. [cite: 142]
"""
import sys
import os
import time
import threading

# Fix path to find 'scn'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scn.hwi.hwi import HardwareInterface as Hwi
from scn.sc.events_publisher import EventsPublisher
from scn.ctrl.handler import LedControl, UdrControl, EventsControl

from event_detection import GripLogic
from led_feedback import LedFeedback
from ui_bridge import UiBridge

class RehabSystem:
    def __init__(self, hwi, events_pub, led_ctrl):
        self.logic = GripLogic()
        self.feedback = LedFeedback(led_ctrl)
        self.ui = UiBridge()
        self.hwi = hwi
        self.led_ctrl = led_ctrl
        events_pub.add_callback(self.run_logic)

    def run_logic(self, events):
        for e in events:
            # Only process Force events 
            if e["id"] in [1, 2, 3]: 
                state = self.logic.analyze_touch(e["value"])
                self.feedback.set_global_color(state)
                self.ui.send(e["sc_id"], state, e["value"])

if __name__ == '__main__':
    hwi = Hwi(Hwi.DefaultConfig())
    hwi.open()
    hwi.ctrl().reader().start()
    hwi.data().reader().start()

    print("Connecting to e-skin...")
    hwi.connect()
    time.sleep(5) 

    # Hardware Configuration 
    UdrControl(hwi).handleCommand("udr 63") 
    time.sleep(1) 
    print("Calibrating... DO NOT TOUCH SKIN.")
    EventsControl(hwi).handleCommand("store offsets") 
    time.sleep(3) 
    EventsControl(hwi).handleCommand("e on") 
    time.sleep(1) 
    LedControl(hwi).handleCommand("of off") 
    time.sleep(1)
    LedControl(hwi).handleCommand("white") 

    rehab_sys = RehabSystem(hwi, EventsPublisher(hwi), LedControl(hwi))
    
    print("\n>>> SYSTEM READY.")
    print("Commands: 'd' to disconnect, 'q' to quit.")

    # CLI Loop 
    while True:
        try:
            cmd = input().strip()
            if cmd == "q":
                break
            elif cmd == "d":
                print("Disconnecting...")
                hwi.disconnect() 
            elif cmd == "c":
                print("Reconnecting...")
                hwi.connect()
            else:
                print(f"Unknown command: {cmd}. Use 'd' or 'q'.")
        except KeyboardInterrupt:
            break

    hwi.close()
    sys.exit(0)