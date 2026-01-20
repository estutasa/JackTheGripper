#!/usr/bin/python3


import logging

from scn.icommand_handler import ICommandHandler,descr_entry
from scn.hwi.hwi import HardwareInterface as Hwi
import scn.ctrl.pkt



class EventsControl(ICommandHandler):

    @property
    def logger(self):
        return logging.getLogger(f"{__name__}.{self.__class__.__name__}")


    def __init__(self,hwi : Hwi):
        self.__hwi = hwi

    # def __del__(self):
    #     pass


    def handleCommand(self,cmd : str) -> bool:
        cmd_parts = cmd.split()
        cmd_len = len(cmd_parts)

        hwi = self.__hwi

        if(cmd == "e on"):
            pkt = scn.ctrl.pkt.E_ON_CMD_PKT
            hwi.ctrl().write(pkt)
            return True
        
        if(cmd == "e off"):
            pkt = scn.ctrl.pkt.E_OFF_CMD_PKT
            hwi.ctrl().write(pkt)
            return True
        
        return False
    

    def commandDescription(self,col_width : int = 30) -> str:
        descr = str() \
            + descr_entry("e <on | off>",     "Enable/Disable event mode.",col_width)
        return descr
