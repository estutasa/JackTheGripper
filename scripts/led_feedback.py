"""
FILE HEADER: led_feedback.py
PURPOSE: Manages real-time visual feedback using the e-skin integrated LEDs.
STRUCTURE: Inherits/Adapts tutorial logic to map detection states to colors.
"""

from scn.ctrl.handler.led_control import COLOR_VAL_MAP

class LedFeedback:
    def __init__(self, led_ctrl):
        """
        PURPOSE: Initialize LED controller.
        INPUTS: led_ctrl - The Skin Cell Network LED control object.
        """
        self.__led_ctrl = led_ctrl

    def update_skin_leds(self, sc_id, state):
        """
        PURPOSE: Set LED color based on the GripLogic state.
        INPUTS: sc_id (int), state (int) from event_detections.py
        OUTPUTS: None (Sets hardware LED)
        """
        # Step 1: Map state to color constant 
        if state == 1:
            color = COLOR_VAL_MAP.get("green") # Good Grip
        elif state == 2:
            color = COLOR_VAL_MAP.get("red")   # Spasm Alert
        else:
            color = COLOR_VAL_MAP.get("blue")  # Idle/Proximity 

        # Step 2: Send command to specific skin cell
        self.__led_ctrl.set_led_color_val(color, sc_id)