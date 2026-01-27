"""
FILE HEADER: event_detection.py
MAIN FUNCTION: GripLogic class for real-time classification.
INPUTS: Force event values from e-skin.
OUTPUTS: Classification state (0: Idle, 1: Good, 2: Bad).
"""
import time

class GripLogic:
    def __init__(self):
        self.last_time = 0
        self.spasm_interval = 0.08 # Adjustable: less than 80ms between touches is "Bad"

    def analyze_touch(self, force_val):
        """
        Analyzes the frequency of events to detect spasms.
        """
        current_time = time.time()
        diff = current_time - self.last_time
        self.last_time = current_time

        if force_val > 0.04: # Threshold to ignore noise
            if diff < self.spasm_interval:
                return 2 # Bad Grip (red)
            return 1 # Good Grip (green)
        return 0 # White (idle)