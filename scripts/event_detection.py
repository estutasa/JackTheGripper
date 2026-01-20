"""
FILE HEADER: event_detection.py
PURPOSE: Implements neuromorphic logic to classify hand-grip interactions.
STRUCTURE: Contains the GripLogic class using temporal frequency analysis.
"""

import time

class GripLogic:
    def __init__(self):
        """
        PURPOSE: Initialize state tracking variables.
        INPUTS: None
        OUTPUTS: None
        """
        self.last_event_time = 0
        self.spasm_frequency = 0.05 # Max time between events for a spasm (20Hz+)

    def analyze_touch(self, force_val):
        """
        PURPOSE: Classify incoming force events as Controlled Grip or Spasm.
        INPUTS: force_val (float) - The force intensity from a skin cell event.
        OUTPUTS: state (int) - 0: Idle, 1: Controlled Grip, 2: Spasm.
        """
        # Step 1: Calculate time elapsed since last event
        current_time = time.time()
        time_diff = current_time - self.last_event_time
        
        # Step 2: Determine state based on temporal frequency and force
        if force_val > 0.04: # Using Force Threshold 
            if time_diff < self.spasm_frequency and self.last_event_time != 0:
                state = 2 # Spasm (High frequency burst)
            else:
                state = 1 # Controlled Grip (Steady intent)
        else:
            state = 0 # No contact
            
        # Step 3: Update timestamp and return
        self.last_event_time = current_time
        return state