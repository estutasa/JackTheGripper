""" 
FILE:ui_bridge.py
Purpose: Acts as a bridge between the data acquisition and the 3D visualization interfac
Maps raw sensor data ino clinical zones and streams intensity vector for real-time tracking
"""

import numpy as np

class UIBridge:
    def __init__(self,visualizer_window):
        """
        Initializes the bridge with a reference to the 3D window
        Inputs:visualizer_window (Visualizator 3D)
        Outputs: none
        """
        self.gui=visualizer_window
        self.zones={"left":range(0,5),"center":range(5,11),"right":range(11,16)}
        self.THRESHOLD_GREEN=0.34

    def process_and_stream(self, raw_scn_data):
        """
        Maps raw hardware data to a 16-sensor intensity vector and streams it to the 3D visualizer
        Inputs: raw_scn_data(dict)
        Outputs: None
        """
        intensity_vector=[0.0]*16
        #Iterating through cell IDs 1-16
        for cell_id,data in raw_scn_data.items():
            raw_val=data.get('force',0)
            normalized=np.clip(raw_val/self.THRESHOLD_GREEN,0,1)
            if 1<=cell_id <=16:
                intensity_vector[cell_id-1]=normalized
        self.gui.comm.data_signal.emit(intensity_vector)
    
    def get_zone_averages(self,intensity_vector):
        """
        Calculates average pressure for each clinical zone from the intensity vector
        Iputus: intensity vector (list)
        Output: dict containaing mean values of each zone (Left,right, center)
        """
        return{
            "Left_Side":np.mean([intensity_vector[i] for i in self.zones["left"]]),
            "Center":np.mean([intensity_vector[i] for i in self.zones["center"]]),
            "Right_side":np.mean([intensity_vector[i] for i in self.zones["right"]])
        }
