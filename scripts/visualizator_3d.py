import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget,QLabel
from PyQt6.QtCore import QTimer
import pyqtgraph.opengl as gl
from PyQt6.QtGui import QVector3D
from stl import mesh
import numpy as np
import time
#Purpose: Renders the 3D handle and e-skin grid. Maps 16 physical sensors to a hight density hexagonal mesh using a heatmap

class Visualizator3D(QMainWindow):
    #Initialize the GUI window, 3D engine, set up camera and load the handle model.
    #INPUTS: file_stl (str): Path to the .STL file to be loaded
    #OUTPUTS: None (Initializes class instance)
    def __init__(self, file_stl):
        super().__init__()
        #Window configuration
        self.setWindowTitle("3D HOMUNCULUS")
        self.resize(1024,768)
        #3D VIEWER setup
        self.viewer=gl.GLViewWidget()
        self.setCentralWidget(self.viewer)
        #Data storage: List to store sensor nodes for the heatamap
        self.sensor_nodes=[]
        #axes representation
        axes=gl.GLAxisItem()
        axes.setSize(x=20,y=20,z=20)
        axes.translate(-50,-50,0)
        self.viewer.addItem(axes)
        #Camera configuation
        self.viewer.opts['center']=QVector3D(0,0,0)
        self.viewer.setCameraPosition(distance=300, elevation=10,azimuth=90)        
        #Load Geometry 
        try:
            #import STL FILE
            my_mesh=mesh.Mesh.from_file(file_stl)
            #From STL to OpenGL
            points=my_mesh.points.reshape(-1,3)
            faces=np.arange(len(points)).reshape(-1,3)
            #Add 3D mesh to the viewer
            self.mesh_item=gl.GLMeshItem(vertexes=points, faces=faces, smooth=True,color=(0.7,0.7,0.7,1.0),shader='normalColor')
            #Rotation
            self.mesh_item.rotate(90,0,0,1)
            self.mesh_item.rotate(-90,0,1,0)
            self.viewer.addItem(self.mesh_item)
            #Add e-skin sensor grid
            self.create_sensor_grid()
        except Exception as e:
            print(f"Error loading STL: {e}")
    
    #Generates hexagones and maps them to 16 physical regions
    #INPUTS:None
    #OUTPUTS:None, items added directly to self.viewer
    def create_sensor_grid(self):
        #Generate "sensors" over semicircle
        rows=14
        cols=16
        #Values our desing
        length=100 #PREGUNTAR SARA LOS VALORES DE NUESTRO CILINDRO
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
                #Angle from 0 to 180 degrees
                angle=start_angle+total_angle*(j/(cols-1))
                 #Coordinates
                x=(i-rows/2)*(length/rows)+offset_x
                y=radius*np.cos(angle)+offset_y
                z=radius*np.sin(angle)+offset_z
                #Geometry e-skin
                hexagon_data  =gl.MeshData.sphere(rows=2,cols=6)
                node=gl.GLMeshItem(meshdata=hexagon_data, smooth=False, color=(0,0,1,1),shader='shaded')
                #Sensors bigger for r=5
                node.scale(5.0,5.0,0.2)
                angle_deg=np.degrees(angle)
                node.rotate(angle_deg+90,1,0,0)

                node.translate(x,y,z)
                node.opts['sensor_id']=j

                if j<5:
                    node.opts['zone']='Left'
                elif j<11:
                    node.opts['zone']='Center'
                else:
                    node.opts['zone']='Right'
                self.viewer.addItem(node)
                self.sensor_nodes.append(node)
    
    #Updates the color of all visual nodes based on a 16-sensor input vector.
    #INPUTS: data_vector (list) - List of 16 pressure values (0.0 to 1.0)
    #OUTPUTS: Nonee
    def update_with_real_data(self,data_vector):
        #Validate input length
        if len(data_vector) !=16:
            return
        #Update each node based on its assigned physical ID
        for node in self.sensor_nodes:
            #Get assigned ID from create_sensor_grid
            physical_id=node.opts['sensor_id']
            intensity=data_vector[physical_id]
            #Apply heatmap (Blue =low, Red=high)
            node.setColor((intensity,0,1-intensity,1))
