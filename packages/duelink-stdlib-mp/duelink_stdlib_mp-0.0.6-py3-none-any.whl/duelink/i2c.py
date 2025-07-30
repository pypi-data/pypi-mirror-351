import duelink as DL

class I2cController:    

    def __init__(self, transport):
        self.transport = transport
        
    def Configuration(self, speed):
        r,s = self.transport.execute(f"i2ccfg({speed})")
        return s

    def Write(self, address, data, offset=0, count=-1):
        if count == -1:
            count = len(data)-offset
        return self.WriteRead(address, data, offset, count, None, 0, 0)
    
    def Read(self, address, data, offset=0, count=-1):
        if count == -1:
            count = len(data)-offset
        return self.WriteRead(address, null, 0, 0, data, offset, count)
    
    def WriteRead(self, address, dataWrite, offsetWrite, countWrite, dataRead, offsetRead, countRead):
        if (dataWrite is None and dataRead is None) or (countWrite == 0 and countRead == 0):
            raise Exception("read or write data must be provided")
        
        if (dataWrite is None and countWrite != 0) or (dataWrite is not None and countWrite+offsetWrite > len(dataWrite)):
            raise Exception("countWrite out of range")
         
        if (dataRead is None and countRead != 0) or (dataRead is not None and countRead+offsetRead > len(dataRead)):
            raise Exception("countRead out of range")
        
        write_array = DL.build_bytearray(dataWrite, offsetWrite, countWrite)
        r,s = self.transport.execute(f"i2cwr({address},{write_array},0)")
        return s