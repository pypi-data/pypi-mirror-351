import time
import machine
import duelink

from duelink import transport

class DuePicoController:    
    def __init__(self):                
        self.due = duelink.DUELinkController(transport.UartTransportController(0))
        
    def StatLed(self, high, low, count):
        self.due.System.StatLed(high, low, count)

 