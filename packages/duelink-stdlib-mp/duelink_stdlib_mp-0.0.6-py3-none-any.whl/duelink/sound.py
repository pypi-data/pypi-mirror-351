import duelink as DL

class SoundController:    
    def __init__(self, transport):
        self.transport = transport

    def Beep(self, pin, frequency, duration_ms):
        r, s = self.transport.execute(f"beep({pin},{frequency},{duration_ms})")
        return s
    
    def MelodyPlay(self, pin, notes):
        arr = ""
        if isinstance(notes, (list)):
            arr = DL.build_floatarray(notes)
        elif isinstance(notes, str):
            arr = notes
        else:
            t = type(notes)
            raise Exception("Invalid notes type '{t}'")

        r, s = self.transport.execute(f"melodyp({pin},{arr})")
        if not s:
            raise Exception(r)
        
    def MelodyStop(self, pin):
        r, s = self.transport.execute(f"melodys({pin})")
        if not s:
            raise Exception(r)
        


