"""
FILE: event_detection.py
PURPOSE: Simple classification for stroke rehab. Categorized raw force data intro three states based on predefined thresholds
"""

class GripLogic:
    def __init__(self):
        """
        Initializes classification thresholds based on clinical research
        Inputs: none
        Outputs:none
        """
        self.STRONG_GRIP = 0.34  # Good pressure -> Green - 9kg target force (clinical research)
        self.STRONG_GRIP = 0.15  # Good pressure -> Green
        self.WEAK_GRIP = 0.05    # Light touch -> Red

    def classify(self, force_val):
        """
        Categorizes a normalized force value into a feedback state
        Input: force_val (normalized maximum force detected)
        Outputs: int. State
        0: White (Idle), 1: Green (Good), 2: Red (Weak)
        """
        if force_val > self.STRONG_GRIP:
            print("GOOD FORCE:", force_val) 
            return 1
        elif force_val > self.WEAK_GRIP:
            print("BAD FORCE:", force_val) 
        0: White (Idle), 1: Green (Good), 2: Red (Weak)
        if force_val > self.STRONG_GRIP:
            return 1
        elif force_val > self.WEAK_GRIP:
            return 2
        return 0