
class SystemController:    

    def __init__(self, transport):
        self.transport = transport

    def Info(self, code):
        r, s = self.transport.execute(f"info({code})")
        if s:
            return float(r)
        return 0
    
    def Reset(self, option):
        self.transport.execute(f"reset({option})")
        
    def StatLed(self, highPeriod, lowPeriod, count):
        r, s = self.transport.execute(f"statled({highPeriod},{lowPeriod},{count})")
        if not s:
            raise Exception(r)
        
    def New(self):
        r, s = self.transport.execute(f"new")
        if not s:
            raise Exception(r)
        
    def SetArrayValue(self, var, data, offset=0, count=-1):
        if count == -1:
            count = len(data)-offset
        if len(var) != 2:
            raise Exception("Invalid array variable")
        
        if (
            (var[0] != 'a' and var[0] != 'A' and var[0] != 'b' and var[0] != 'B')
            or (var[1] < '0' or var[1] > '9')
        ):
            raise Exception("Invalid array variable must be A0..A9 or B0..B9")
                                                                                                         
        r, s = self.transport.execute(f"dim {var}[{count}]")
        r, s = self.transport.execute(f"strmwr({var},{count})")
        if not s:
            raise Excpetion(r)
        if count > 0:
            if var[0] == 'b':
                self.transport.streamOutBytes(data[offset:offset+count])
            elif var[0] == 'a':
                self.transport.streamOutFloats(data[offset:offset+count])
        
        
