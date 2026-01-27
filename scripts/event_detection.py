"""
FILE HEADER: event_detection.py
MAIN FUNCTION: GripLogic class for real-time intensity classification.
INPUTS: Force event values from e-skin.
OUTPUTS: Classification state (0: Idle, 1: Good/High, 2: Bad/Low).
"""
import time

class GripLogic:
    def __init__(self):
        # Thresholds: Adjust these based on your specific e-skin sensitivity
        self.GOOD_FORCE_THRESHOLD = 0.12  # Squeeze hard for Green
        self.MIN_CONTACT_THRESHOLD = 0.02 # Minimal touch for Red

    def analyze_touch(self, force_val):
        """
        Analyzes force intensity to guide the user. [cite: 181]
        """
        if force_val > self.GOOD_FORCE_THRESHOLD:
            return 1  # Good Grip -> Green
        elif force_val > self.MIN_CONTACT_THRESHOLD:
            return 2  # Bad/Weak Grip -> Red
        else:
            return 0  # Idle -> White