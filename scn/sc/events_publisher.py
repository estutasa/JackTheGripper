#!/usr/bin/python3


import logging
import threading
from typing import Callable, Dict, List, Tuple, TypedDict

from scn.icommand_handler import ICommandHandler,descr_entry
from scn.hwi.hwi import HardwareInterface as Hwi
from scn.core import mask, print_hex_block
import scn.ctrl.pkt

import scn.sc.pkt.events


class EventsPublisher:
    ScEvent = scn.sc.pkt.events.Event
    ScEvents = List[ScEvent]

    Callback = Callable[[ScEvents],None]
    CallbackList = List[Callback]

    EVENT_ID_PROX   = scn.sc.pkt.events.EVENT_ID_PROX
    EVENT_ID_FORCE1 = scn.sc.pkt.events.EVENT_ID_FORCE1
    EVENT_ID_FORCE2 = scn.sc.pkt.events.EVENT_ID_FORCE2
    EVENT_ID_FORCE3 = scn.sc.pkt.events.EVENT_ID_FORCE3
    EVENT_ID_ACCX   = scn.sc.pkt.events.EVENT_ID_ACCX
    EVENT_ID_ACCY   = scn.sc.pkt.events.EVENT_ID_ACCY
    EVENT_ID_ACCZ   = scn.sc.pkt.events.EVENT_ID_ACCZ
    EVENT_ID_TEMP   = scn.sc.pkt.events.EVENT_ID_TEMP

    @property
    def logger(self):
        return logging.getLogger(f"{__name__}.{self.__class__.__name__}")


    def __init__(self,hwi : Hwi):
        self.__hwi = hwi
        self.__cb_list : EventsPublisher.CallbackList = []
        self.__mutex = threading.Lock()

        hwi.data().reader().add_callback(self.__event_packets_handler)

    # def __del__(self):
    #     pass


    def add_callback(self, cb : Callback):
        with self.__mutex:
            self.__cb_list.append(cb)


    def __event_packets_handler(self,pkt : bytes):
        if pkt[0] != 0xE2:
            return
        
        sc_events = scn.sc.pkt.events.get_events(pkt)
        
        with self.__mutex:

            for cb in self.__cb_list:
                cb(sc_events)

        # print(f"sc events:")
        # print_hex_block(pkt)


        pass

