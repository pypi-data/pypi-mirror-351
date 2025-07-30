import machine
import time

from duelink.digital import DigitalController
from duelink.led import LedController
from duelink.analog import AnalogController
from duelink.button import ButtonController
from duelink.system import SystemController
from duelink.sound import SoundController
from duelink.graphics import GraphicsController, GraphicsType
from duelink.i2c import I2cController
from duelink.frequency import FrequencyController
from duelink.sound import SoundController

   
class DUELinkController:
    def __init__(self, transport):
        self.transport = transport
        self.Digital = DigitalController(self.transport)
        self.Led = LedController(self.transport)
        self.Analog = AnalogController(self.transport)
        self.Button = ButtonController(self.transport)
        self.System = SystemController(self.transport)
        self.Sound = SoundController(self.transport)
        self.Graphics = GraphicsController(self.transport)
        self.I2c = I2cController(self.transport)
        self.Frequency = FrequencyController(self.transport)
        self.Sound = SoundController(self.transport)
    
    
    


