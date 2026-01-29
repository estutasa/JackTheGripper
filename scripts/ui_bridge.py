import numpy as np

class UIBridge:
    def __init__(self,visualizer_window):
        #Initializes the bridge with a reference to the 3D window
        #Inputs:visualizer_window. The instance of Visualizator3D
        self.gui=visualizer_window
        #Define clinical zones
        self.zones={"left":range(0,5),"center":range(5,11),"right":range(11,16)}
        self.THRESHOLD_GREEN=0.34

    def process_and_stream(self, raw_scn_data):
        #Maps raw hardware data to a 16-senosr intensity vector. 
        #Inputs: raw_scn_data(dict)-Data received from the WIFI interface
        #Initialize 16 sensors (5-6-5 layour logic happens here)
        intensity_vector=[0.0]*16
        #Iterating through cell IDs 1-16 
        for cell_id,data in raw_scn_data.items():
            #Extract sensor value (eg. proximity or force)
            raw_val=data.get('force',0)
            #Normalize: Assuming 0-500 is the typical rae range
            normalized=np.clip(raw_val/self.THRESHOLD_GREEN,0,1)
            if 1<=cell_id <=16:
                intensity_vector[cell_id-1]=normalized
        self.gui.comm.data_signal.emit(intensity_vector)
    
    def get_zone_averages(self,intensity_vector):
        #Calculaes average pressure for 5-6-5 zones.
        #Output: gui labels

        return{
            "Left_Side":np.mean([intensity_vector[i] for i in self.zones["left"]]),
            "Center":np.mean([intensity_vector[i] for i in self.zones["center"]]),
            "Right_side":np.mean([intensity_vector[i] for i in self.zones["right"]])
        }