import time
import machine
import mDUELink

from mDUELink import transport

class DuePicoController:    
    def __init__(self):                
        self.due = mDUELink.DUELinkController(transport.UartTransportController(0))
        
    def StatLed(self, high, low, count):
        self.due.System.StatLed(high, low, count)

 