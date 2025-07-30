import duelink as DL

class GraphicsType:
    I2c = 1
    Spi = 2
    Neo = 3
    Matrix5x5 = 4
    
class GraphicsController:
    def __init__(self, transport):
        self.transport = transport

    def Configuration(self, type, config, width, height, mode):
        cfg_array = "{"
        for n in config:
            if len(cfg_array)>1:
                cfg_array = cfg_array + ","
            cfg_array = cfg_array + str(n)
        cfg_array = cfg_array + "}"
        
        r, s = self.transport.execute(f"gfxcfg({type},{cfg_array},{width},{height},{mode})")
        return s
    
    def Show(self):
        r, s = self.transport.execute("show()")
        return s
    
    def Clear(self, color):
        r, s = self.transport.execute(f"clear({color})")
        return s
    
    def Pixel(self, color, x, y):
        r, s = self.transport.execute(f"pixel({color},{x},{y})")
        return s
    
    def Circle(self, color, x, y, r):
        r, s = self.transport.execute(f"circle({color},{x},{y},{r})")
        return s
    
    def Rect(self, color, x, y, w, h):
        r, s = self.transport.execute(f"rect({color},{x},{y},{w},{h})")
        return s
    
    def Fill(self, color, x, y, w, h):
        r, s = self.transport.execute(f"fill({color},{x},{y},{w},{h})")
        return s
    
    def Line(self, color, x1, y1, x2, y2):
        r, s = self.transport.execute(f"line({color},{x1},{y1},{x2},{y2})")
        return s
        
    def Text(self, text, color, x, y):
        r, s = self.transport.execute(f"text(\"{text}\",{color},{x},{y})")
        return s
        
    def TextS(self, text, color, x, y, sx, sy):
        r, s = self.transport.execute(f"texts(\"{text}\",{color},{x},{y},{sx},{sy})")
        return s
    
    def TextT(self, text, color, x, y):
        r, s = self.transport.execute(f"textt(\"{text}\",{color},{x},{y})")
        return s
    
    def DrawImage(self, img, x, y, w, h, transform):
        return self.DrawImageScale(img, x, y, w, h, 1, 1, transform)
    
    def DrawImageScale(self, img, x, y, w, h, sx, sy, transform):
        if (img is None or w<=0 or h<=0):
            raise Exception("Invalid argument")
        img_arr = ""
        if isinstance(img, (list)):
            img_arr = DL.build_floatarray(img)
        elif isinstance(img, str):
            img_arr = img
        else:
            t = type(img)
            raise Exception("Invalid image type '{t}'")
        
        r, s = self.transport.execute(f"imgs({img_arr},{x},{y},{w},{h},{sx},{sy},{transform})")
        return s
            