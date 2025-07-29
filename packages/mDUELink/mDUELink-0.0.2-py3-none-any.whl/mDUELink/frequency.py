
class FrequencyController:    
    def __init__(self, transport):
        self.transport = transport

    def Write(self, pin, frequency, duration_ms, duty = 0.5):
        if frequency < 15 or frequency > 10000000:
            raise Exception("Frequency must bin range 15Hz..10,000,000Hz")
        if duty < 0 or duty > 1:
            raise Exception("Duty cycle must be in range 0..1")
        
        r, s = self.transport.execute(f"freq({pin},{frequency},{duration_ms},{duty})")
        return s

