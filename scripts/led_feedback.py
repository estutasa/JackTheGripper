"""
FILE HEADER: led_feedback.py
PURPOSE: Maps Grip state to global LED colors (Green/Red/White).
"""
from scn.ctrl.handler.led_control import COLOR_VAL_MAP

class LedFeedback:
    def __init__(self, led_ctrl):
        self.__led_ctrl = led_ctrl

    def set_global_color(self, state):
        """
        OUTPUTS: Sets all LEDs to Green (1), Red (2), or White (0).
        """
        if state == 1:
            color = COLOR_VAL_MAP.get("green")
        elif state == 2:
            color = COLOR_VAL_MAP.get("red")
        else:
            color = COLOR_VAL_MAP.get("white") # 

        self.__led_ctrl.set_led_color_val(color)