
class ButtonController:    

    def __init__(self, transport):
        self.transport = transport

    def Enable(self, pin, state):
        if state :
            self.transport.execute(f"btnenable({pin},1)")
        else:
            self.transport.execute(f"btnenable({pin},0)")
            
    def Up(self, pin):
        r, s = self.transport.execute(f"btnup({pin})")
        if s:
            return r[0] == '1'
        return 0
    
    def Down(self, pin):
        r, s = self.transport.execute(f"btndown({pin})")
        if s:
            return r[0] == '1'
        return 0
