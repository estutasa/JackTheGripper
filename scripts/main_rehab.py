"""
FILE HEADER: main_rehab.py
PURPOSE: Main entry point for the Stroke Rehab Handle.
STRUCTURE: Connects Hardware, Logic, Feedback, and UI modules.
"""

from event_detection import GripLogic
from led_feedback import LedFeedback
from ui_bridge import UiBridge
# Import SCN libraries here [cite: 140]

class RehabSystem:
    def __init__(self, hwi, events_pub, led_ctrl):
        """
        PURPOSE: Initialize all sub-modules and subscribe to event stream.
        """
        self.logic = GripLogic()
        self.feedback = LedFeedback(led_ctrl)
        self.ui = UiBridge()
        events_pub.add_callback(self.run_logic)

    def run_logic(self, events):
        """
        PURPOSE: The main loop callback triggered by skin events[cite: 100].
        INPUTS: events - List of skin cell events.
        """
        for e in events:
            # Step 1: Extract data
            sc_id = e["sc_id"]
            val = e["value"]
            
            # Step 2: Process through Esther's Logic
            state = self.logic.analyze_touch(val)
            
            # Step 3: Trigger Laura's LEDs
            self.feedback.update_skin_leds(sc_id, state)
            
            # Step 4: Stream to Natalia's UI
            self.ui.format_for_gui(sc_id, state, val)