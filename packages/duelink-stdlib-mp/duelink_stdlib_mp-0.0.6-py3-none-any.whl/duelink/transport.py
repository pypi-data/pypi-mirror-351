import machine
import time
import struct

class I2CTransportController:
    def __init__(self, sda, scl, i2ccontroller=1, freq=400000, addr=0x52):
        self.i2c = machine.I2C(i2ccontroller, sda = sda, scl = scl, freq=freq)
        self.addr = addr
    
    def writeBytes(self, bytes):
        self.i2c.writeto(self.addr, array.array(bytes))
        
    def write(self, str):
        self.i2c.writeto(self.addr, str+"\n")
        
    def read(self, buf, timeout):
        startms = time.ticks_ms()
        bytesToRead = 0;
        i=0
        while (time.ticks_ms() - startms < timeout):
            bytes = self.i2c.readfrom(self.addr, 1)
            if bytes is not None and len(bytes) > 0:
                c = bytes[0]
                if c >= 0 and c <= 127:
                    bytesToRead=len(buf)-2
                    buf[i] = c
                    i = i + 1
                    break
        if bytesToRead > 0 and buf[0] != '>' and buf[0] != '&':
            bytes = self.i2c.readfrom(self.addr, bytesToRead)
            while (time.ticks_ms() - startms < timeout) and bytesToRead > 0:
                for c in bytes:
                    if c >= 0 and c <= 127:
                        buf[i] = c
                        i = i + 1
                        bytesToRead = bytesToRead - 1
                        if bytesToRead == 0:
                            break
    
    def execute(self, command):
        buf = bytearray(128)
        self.write(command)
        self.read(buf, 1000)
        return self.__getResponse(command, buf.decode("utf-8"))
        
    def __getResponse(self, command, response):
        cmdIdx = response.find(command)
        if cmdIdx == -1:
            cmdIdx = 0
        else:
            cmdIdx = len(command)+2 # +2 skip \r\n
        
        success = response[cmdIdx] != '!'
        if not success:
            cmdIdx = cmdIdx + 1
            
        if response[cmdIdx] == '>':
            return ("", success)
        
        endIdx = response.find("\r\n>", cmdIdx)
        if endIdx >= cmdIdx:
            return (response[cmdIdx:endIdx], success)
        
        return ("", success)
    
class UartTransportController:
    def __init__(self, id):
        self.uart = machine.UART(id,115200)
        self.uart.init(115200, bits=8, parity=None, stop=1, timeout=1000)
        time.sleep(0.2)
        self.sync()
        
    def sync(self):
        self.uart.write(b'\x1b')
        bytes = self.uart.read(3)
        if bytes is None or len(bytes)<3 or bytes[2] != 62:
            raise Exception("DUELink not responding")
    
    def write(self, str):
        self.uart.write(str+"\n")
        
    def read(self, buf, timeout):
        startms = time.ticks_ms()
        bytesToRead = 0;
        i=0
        while (time.ticks_ms() - startms < timeout):
            bytes = self.uart.read(1)
            if bytes is not None and len(bytes) > 0:
                c = bytes[0]
                if c >= 0 and c <= 127:
                    bytesToRead=len(buf)-2
                    buf[i] = c
                    i = i + 1                    
                    break
        if bytesToRead > 0 and buf[0] != ord('>') and buf[0] != ord('&'):
            while (time.ticks_ms() - startms < timeout and bytesToRead > 0):
                bytes = self.uart.read(1)
                if bytes is None or len(bytes) == 0:
                    break
                c = bytes[0]
                if c >= 0 and c <= 127:
                    bytesToRead=bytesToRead-1                    
                    buf[i] = c
                    i = i + 1
                    if i>=3 and c == ord('>') and buf[i-2] == ord('\n') and buf[i-3] == ord('\r'):
                        break
    
    def execute(self, command):
        buf = bytearray(128)
        self.write(command)
        self.read(buf, 1000)
        return self.__getResponse(command, buf.decode("utf-8"))
    
    def streamOutBytes(self, bytes):
        buf = bytearray(128)
        self.uart.write(bytearray(bytes))
        self.read(buf, 1000)
        return self.__getResponse("", buf.decode("utf-8"))
    
    def streamOutFloats(self, floats):
        buf = bytearray(128)
        for f in floats:
            bf = struct.pack("<f",f)            
            self.uart.write(bf)   
        self.read(buf, 1000)
        return self.__getResponse("", buf.decode("utf-8"))
        
    def __getResponse(self, command, response):
        cmdIdx = response.find(command)
        if cmdIdx == -1:
            cmdIdx = 0
        else:
            cmdIdx = len(command)+2 # +2 skip \r\n
        
        success = response[cmdIdx] != '!'
        if not success:
            cmdIdx = cmdIdx + 1
            
        if response[cmdIdx] == '>' or response[cmdIdx] == '&':
            return ("", success)
        
        endIdx = response.find("\r\n>", cmdIdx)
        if endIdx >= cmdIdx:
            return (response[cmdIdx:endIdx], success)
        
        return ("", success)
    
