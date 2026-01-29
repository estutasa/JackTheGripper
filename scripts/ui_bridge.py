"""
FILE HEADER: ui_bridge.py
PURPOSE: Standardizes data stream for the Homunculus GUI
"""
class UiBridge:
    def send(self, sc_id, state, val):
        """
        Outputs data formatted for capture by the GUI module
        INPUTS: sc_id (cell ID), state (classification), val (force value)
        """
        print(f"DATA|ID:{sc_id}|ST:{state}|VAL:{val:.4f}")