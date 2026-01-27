"""
FILE HEADER: ui_bridge.py
PURPOSE: Bridges the real-time event stream to the GUI visualization.
STRUCTURE: Formats data packets for the Tactile Homunculus[cite: 47].
"""

class UiBridge:
    def format_for_gui(self, sc_id, state, val):
        """
        PURPOSE: Print standardized strings for the GUI to parse.
        INPUTS: sc_id (int), state (int), val (float).
        OUTPUTS: Formatted string to stdout.
        """
        # Step 1: Build data packet string
        packet = f"UI_DATA|SC:{sc_id}|STATE:{state}|VAL:{val:.4f}"
        
        # Step 2: Output for external GUI script capture
        # print(packet)