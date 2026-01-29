import threading
import time
from scn.ctrl.handler.led_control import COLOR_VAL_MAP
from scn.sc.pkt.data import data_tuple_to_data1200
from event_detection import GripLogic
from ui_bridge import UIBridge

class LedFeedbackRehab:
    def __init__(self, hwi, data_pub, led_ctrl, visualizer=None):
        self.__hwi = hwi
        self.__data_pub = data_pub
        self.__led_ctrl = led_ctrl
        self.logic = GripLogic()
        #Connexion UI
        self.bridge=None
        if visualizer:
            self.bridge=UIBridge(visualizer)
        self.__started = False
        self.__thread = None
        self.__stop_event = threading.Event()
        self.__mutex = threading.Lock()
        self.__current_color = COLOR_VAL_MAP.get("white")

    def start(self):
        if not self.__started:
            self.__stop_event.clear()
            self.__thread = threading.Thread(target=self.__run)
            self.__thread.start()
            self.__started = True

    def stop(self):
        if self.__started:
            self.__stop_event.set()
            if self.__thread.is_alive():
                self.__thread.join()
            self.__started = False
            self.__led_ctrl.set_led_color_val(COLOR_VAL_MAP.get("white"))

    def isStarted(self): return self.__started

    def __update(self):
        sc_data_list = self.__data_pub.sc_data()
        if not sc_data_list: return

        raw_data_dict = {}
        max_f = 0.0
        
        for sc_data in sc_data_list:
            # 1. sc_data es una tupla, el ID es el primer elemento (índice 0)
            cell_id = sc_data[0] 
            
            # 2. Convertimos el resto de datos
            d = data_tuple_to_data1200(sc_data)
            
            # 3. Extraemos la fuerza máxima
            f_val_cell = max(d.get("force", [0.0]))
            
            # 4. Guardamos en el diccionario para tu 3D
            if 1 <= cell_id <= 16:
                raw_data_dict[cell_id] = {"force": f_val_cell}
            
            if f_val_cell > max_f: 
                max_f = f_val_cell

        # 5. ENVIAR AL 3D
        if self.bridge:
            self.bridge.process_and_stream(raw_data_dict)

        # 6. Lógica de LEDs
        state = self.logic.classify(max_f)
        
        with self.__mutex:
            if state == 1: 
                self.__current_color = COLOR_VAL_MAP.get("green")
            elif state == 2: 
                self.__current_color = COLOR_VAL_MAP.get("red")
            else: 
                self.__current_color = COLOR_VAL_MAP.get("white")

                
    def __run(self):
        while not self.__stop_event.is_set():
            self.__update()
            with self.__mutex:
                color = self.__current_color
            self.__led_ctrl.set_led_color_val(color)
            time.sleep(0.04) # 25 Hz update rate