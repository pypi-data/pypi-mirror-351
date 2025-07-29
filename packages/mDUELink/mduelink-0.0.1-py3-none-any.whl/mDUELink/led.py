
class LedController:    

    def __init__(self, transport):
        self.transport = transport

    def Set(self, high, low, count):
        self.transport.execute(f"statled({high},{low},{count})")        

