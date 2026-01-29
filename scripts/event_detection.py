"""
FILE: event_detection.py
PURPOSE: Simple classification for stroke rehab.
"""

class GripLogic:
    def __init__(self):
        # Once 'store offsets' is run, these values start from 0.0
        self.STRONG_GRIP = 0.15  # Good pressure -> Green
        self.WEAK_GRIP = 0.05    # Light touch -> Red

    def classify(self, force_val):
        """
        0: White (Idle), 1: Green (Good), 2: Red (Weak)
        """
        if force_val > self.STRONG_GRIP:
            return 1
        elif force_val > self.WEAK_GRIP:
            return 2
        return 0