
class AnalogController:    

    def __init__(self, transport):
        self.transport = transport

    def VRead(self, pin, pull):
        r, s = self.transport.execute(f"vread({pin})")
        if s:
            return float(r)
        return 0
    
    def PWrite(self, pin, power):
        self.transport.execute(f"pwrite({pin},{power})")
