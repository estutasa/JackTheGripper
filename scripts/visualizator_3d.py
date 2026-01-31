"""
FILE: visualizator_3d.py
PURPOSE: Provides 3D visualizaion of the e-skin handle and real-time performance tracking. Provides visual feedback
"""


import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget,QLabel
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, Qt
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from PyQt6.QtGui import QVector3D
from stl import mesh
import numpy as np
import time
class DataComm(QObject):
    #Facilitates thread-safe communication of sensor data
    data_signal=pyqtSignal(list)

class Visualizator3D(QMainWindow):
    #Initialize the GUI window, 3D engine, set up camera, load the handle model and performance chart
    #INPUTS: file_stl (str)
    #OUTPUTS: None 
    def __init__(self, file_stl):
        super().__init__()
        self.setWindowTitle("3D HOMUNCULUS")
        self.resize(1024,768)

        self.container=QWidget()
        self.setCentralWidget(self.container)
        self.layout=QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        #3D VIEWER setup
        self.viewer=gl.GLViewWidget()
        self.layout.addWidget(self.viewer, stretch=3)

        self.feedback_label=QLabel("Grip Stronger")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setStyleSheet("font-size: 30px; font-weight: bold; color: #FF4444; background-color: black; padding: 10px;")
        self.layout.addWidget(self.feedback_label)
        #Performance chart
        self.plot_widget=pg.PlotWidget(title="Performance Tracking")
        self.plot_widget.setBackground('k')
        self.plot_widget.setYRange(0, 1.0)
        self.layout.addWidget(self.plot_widget, stretch=1)
        self.target_line = pg.InfiniteLine(pos=0.34, angle=0, pen=pg.mkPen('y', width=2, style=Qt.PenStyle.DashLine))
        self.plot_widget.addItem(self.target_line)

        self.data_history=[]
        self.curve=self.plot_widget.plot(pen=pg.mkPen('w', width=2))

        self.sensor_nodes=[]
        #axes representation
        axes=gl.GLAxisItem()
        axes.setSize(x=20,y=20,z=20)
        axes.translate(-50,-50,0)
        self.viewer.addItem(axes)
        #Camera configuation
        self.viewer.opts['center']=QVector3D(0,0,0)
        self.viewer.setCameraPosition(distance=300, elevation=10,azimuth=90)        
        self.viewer.setBackgroundColor('k')

        #Load Geometry 
        try:

            my_mesh=mesh.Mesh.from_file(file_stl)
            points=my_mesh.points.reshape(-1,3)
            faces=np.arange(len(points)).reshape(-1,3)
            self.mesh_item=gl.GLMeshItem(vertexes=points, faces=faces, smooth=True,color=(0.85,0.85,0.85,1.0),shader='normalColor')
            self.mesh_item.rotate(90,0,0,1)
            self.mesh_item.rotate(-90,0,1,0)
            self.viewer.addItem(self.mesh_item)

            self.comm = DataComm()
            self.comm.data_signal.connect(self.update_with_real_data)
            self.create_sensor_grid()
            self.timer=QTimer()
            #self.timer.timeout.connect(self.run_dummy_stimulation)
            #self.timer.start(100)
        except Exception as e:
            print(f"Error loading STL: {e}")
    
   
    def create_sensor_grid(self):
         #Generates hexagones and maps them to 16 physical regions
        #INPUTS:None
        #OUTPUTS:None
        left_ids=[3,5,7,9,11]
        right_ids=[1,16,15,14,13]
        center_ids=[2,4,6,8,10,12]
        #Generate "sensors" over semicircle
        rows=14
        cols=16
        length=100
        radius=25.5
        #Move mesh to be aling with STL design
        offset_y=25
        offset_x=-45
        offset_z=-25
        #Coverage angle
        total_angle=np.pi+0.9
        start_angle=-0.45
        #Node generation loop
        for i in range(rows):
            for j in range(cols):

                if i < 5: 
                    ids_zona = right_ids
                    sensor_id = ids_zona[min(j // 4, 4)] 
                elif i < 10: 
                    ids_zona = center_ids
                    sensor_id = ids_zona[min(j // 3, 5)]
                else:
                    ids_zona = left_ids
                    sensor_id = ids_zona[min(j // 4, 4)]

                angle=start_angle+total_angle*(j/(cols-1))
                x=(i-rows/2)*(length/rows)+offset_x
                y=radius*np.cos(angle)+offset_y
                z=radius*np.sin(angle)+offset_z
                #Geometry e-skin
                hexagon_data  =gl.MeshData.sphere(rows=2,cols=6)
                node=gl.GLMeshItem(meshdata=hexagon_data, smooth=False, color=(0.6,0.6,0.6,1),shader='shaded')
                node.scale(5.0,5.0,0.2)
                angle_deg=np.degrees(angle)
                node.rotate(angle_deg+90,1,0,0)

                node.translate(x,y,z)
                node.opts['sensor_id']=sensor_id
                self.viewer.addItem(node)
                self.sensor_nodes.append(node)
    
    def update_with_real_data(self,data_vector):
        #Updates the color of all visual nodes based on a 16-sensor input vector, feedback label and performance chart
        #INPUTS: data_vector (list)
        #OUTPUTS: Nonee
        if len(data_vector) !=16:
            return
        threshold=0.33
        weak_threshold=0.05
        avg_intensity = sum(data_vector) / 16
        if avg_intensity<weak_threshold:
            self.feedback_label.setText("PLEASE GRIP")
            self.feedback_label.setStyleSheet("font-size: 30px; font-weight: bold; color: #FFFFFF; background-color: black; padding: 10px;")
        elif avg_intensity >= threshold:
            self.feedback_label.setText("GOOD JOB!")
            self.feedback_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #00FF00; background-color: black; padding: 10px;")
        else:
            self.feedback_label.setText("Grip stronger")
            self.feedback_label.setStyleSheet("font-size: 30px; font-weight: bold; color: #FF4444; background-color: black; padding: 10px;")
        #Update each node based on its assigned physical ID
        for node in self.sensor_nodes:

            physical_id=node.opts['sensor_id']
            intensity=data_vector[physical_id-1]
            if intensity >= threshold:
                node.setColor((0.0, 0.0, 8, 1))
            else:
                #increase progressively
                red = 0.6 * (1 - intensity)
                green = 0.6 * (1 - intensity)
                blue = 0.6 + (0.4 * intensity)
                node.setColor((red, green, blue, 1))
        
        #Update graph
        try:
            self.data_history.append(sum(data_vector)/16)
            if len(self.data_history) > 100: self.data_history.pop(0)
            self.curve.setData(self.data_history)
        except:
            pass

    """def run_dummy_stimulation(self):
        #Genrate fake 16-sensor variable to test heatmap
        test_vector = [0.1]*16
        for sid in [2, 3, 6, 8, 10, 12]: test_vector[sid-1] = 0.4
        self.comm.data_signal.emit(test_vector)"""


"""
if __name__=="__main__":
    app=QApplication(sys.argv)
    window=Visualizator3D('cylinder_5cm.STL')
    window.show()
    window.timer.start(100)
    sys.exit(app.exec())
    """
     
