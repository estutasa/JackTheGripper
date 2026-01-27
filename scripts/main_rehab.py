"""
FILE HEADER: main_rehab.py
PURPOSE: Main entry point for the Stroke Rehab Handle. Automates setup.
"""
import sys
import os
import time

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
        """
        PURPOSE: Initialize modules and set default white color.
        """
        self.logic = GripLogic()
        self.feedback = LedFeedback(led_ctrl)
        self.ui = UiBridge()
        
        # Seteamos blanco inicial 
        led_ctrl.handleCommand("white") 
        events_pub.add_callback(self.run_logic)

    def run_logic(self, events):
        """
        PURPOSE: Process events and update global color.
        """
        for e in events:
            # Solo procesamos eventos de fuerza 
            if e["id"] in [1, 2, 3]: 
                state = self.logic.analyze_touch(e["value"])
                # Actualiza toda la piel a verde o rojo
                self.feedback.set_global_color(state)
                # Envía datos a Natalia
                self.ui.send(e["sc_id"], state, e["value"])

if __name__ == '__main__':
    hwi = Hwi(Hwi.DefaultConfig())
    hwi.open()
    hwi.ctrl().reader().start()
    hwi.data().reader().start()

    print("Conectando a la e-skin...")
    hwi.connect() # Auto 'c'
    time.sleep(2) 

    # Comandos automáticos de configuración 
    UdrControl(hwi).handleCommand("udr 63") 
    EventsControl(hwi).handleCommand("e on") 
    LedControl(hwi).handleCommand("of off") 

    rehab_sys = RehabSystem(hwi, EventsPublisher(hwi), LedControl(hwi))
    
    print("Sistema listo. Esperando agarre...")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        hwi.close()