import machine
import time

from mDUELink.digital import DigitalController
from mDUELink.led import LedController
from mDUELink.analog import AnalogController
from mDUELink.button import ButtonController
from mDUELink.system import SystemController
from mDUELink.sound import SoundController
from mDUELink.graphics import GraphicsController, GraphicsType
from mDUELink.i2c import I2cController
from mDUELink.frequency import FrequencyController
from mDUELink.sound import SoundController

   
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
    
    
    


