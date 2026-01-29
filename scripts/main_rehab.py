#!/usr/bin/python3
import logging
import sys
import os
import time

# Path fix for SCN library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scn.hwi.hwi import HardwareInterface as Hwi
from scn.ctrl.handler import LedControl, UdrControl, CfControl, IdControl, SensControl, EventsControl
from scn.sc.data_publisher import DataPublisher
from led_feedback import LedFeedbackRehab

if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    
    hwi = Hwi(Hwi.DefaultConfig())
    hwi.open()
    hwi.ctrl().reader().start()
    hwi.data().reader().start()

    data_pub = DataPublisher(hwi)
    led_ctrl = LedControl(hwi)
    
    # Handlers list updated to include EventsControl for 'store offsets'
    handlers = [IdControl(hwi), SensControl(hwi), CfControl(hwi), 
                UdrControl(hwi), led_ctrl, EventsControl(hwi)]

    rehab_sys = LedFeedbackRehab(hwi, data_pub, led_ctrl)

    print(">>> JACK THE GRIPPER: READY <<<")
    print("Sequence: c -> udr 63 -> store offsets -> tut on")

    while True:
        try:
            cmd = input().strip()
            if not cmd: continue
            if cmd == "q": break
            if cmd == "d":
                rehab_sys.stop()
                hwi.disconnect()
                print("Disconnected.")
                continue
            if cmd == "c":
                data_pub.reset()
                hwi.connect()
                continue
            if cmd == "tut on":
                rehab_sys.start()
                print("Rehab logic ACTIVE.")
                continue
            if cmd == "tut off":
                rehab_sys.stop()
                print("Rehab logic INACTIVE.")
                continue

            # Command handler (handles 'store offsets', 'udr 63', etc.)
            handled = False
            for h in handlers:
                if h.handleCommand(cmd):
                    handled = True
                    break
            if not handled:
                print(f"Unknown command: {cmd}")
                
        except KeyboardInterrupt:
            break

    rehab_sys.stop()
    hwi.close()
    sys.exit(0)