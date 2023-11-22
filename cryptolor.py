from PIL import Image
from PIL.PngImagePlugin import PngInfo
from PIL import ImageOps
import random
import json
import sys
import base64
from io import BytesIO
import zlib

class Seed:
    def __init__(self, seed):
        self.bits = self.genBits(seed)
        self.index = 0
        
    def genBits(self,seed):
        out = ""
        bytes = seed.encode('utf-8')
        for b in bytes:
            out = out + str(bin(b))[2:].zfill(8)
        return out
        
    def getBits(self, num):
        i = 0
        out = ""
        while i < num:
            out = out + self.bits[self.index]
            self.index = self.index + 1
            i = i + 1
            if self.index > len(self.bits) - 1:
                self.index = 0
        return out
        
    def getInt(self, numbits):
        return int(self.getBits(numbits), 2)
        
class Points:
    def __init__(self, width, height, seed, checkered=False, box=None):
        self.seed = seed
        self.width = width
        self.height = height
        self.points = []
        self.chunks = []
        if checkered:
            self.genCheckered()
        elif box != None:
            self.genBox(box)
        else:
            self.genPoints()
        self.index = 0
        
    def genBox(self, box_size):
        for y in range(0, self.height, box_size):
            for x in range(0, self.width, box_size):
                self.points.append((x,y))

        for point in self.points:
            chunk = []
            x,y = point
            for i in range(box_size):
                dy = y + i
                for j in range(box_size):
                    dx = x + j
                    new_point = (dx, dy)
                    if new_point != point and dx <= (self.width - 1) and dy <= (self.height - 1):
                        chunk.append(new_point)
            self.chunks.append(chunk)
            
    def genCheckered(self):
        for y in range(0, self.height):
            for x in range(0, self.width - 1, 2):
                self.points.append((x,y))

    def genPoints(self):
        x = 0
        y = 0
        self.seed.getBits(5)
        next = 0
        while (x < self.width - 1) and (y < self.height - 1):
            test = self.seed.getInt(2)
            if test == 0:
                next = self.seed.getInt(8)
            elif test == 1:
                self.seed.getInt(1)
                next = self.seed.getInt(4)
            elif test == 2:
                self.seed.getInt(2)
                next = self.seed.getInt(2)
            elif test == 3:
                self.seed.getInt(3)
                next = self.seed.getInt(4)
            if next > 1:
                x = x + next
                if x >= self.width - 1:
                    x = x - (self.width - 1)
                    y = y + 1
                else:
                    self.points.append((x,y))
    def getPoint(self):
        if self.index > len(self.points) - 1:
            return None
        else:
            self.index = self.index + 1
            return self.points[self.index - 1]
            
class Cryptolor:
    def __init__(self, infile, scale=False, width=1920, height=1080, color=None, seed="tuple", encode_factor=4, print=True, checkered=False, box=None, gzip=False):
        self.checkered = checkered
        self.box = box
        self.gzip = gzip
        self.decoded = None
        self.print = print
        if infile == None:
            if color == None:
                color = self.getRandColor()
            self.input_image = Image.new("RGB", (width, height), color)
            self.width = width
            self.height = height
        else:
            self.input_image = Image.open(infile)
            if scale:
                self.input_image = ImageOps.contain(self.input_image, (width, height))
            self.width, self.height = self.input_image.size
            
        self.input_pix = self.input_image.load()
        
        self.out_image = Image.new("RGB", (self.width, self.height), "white")
        self.out_pix = self.out_image.load()
        self.seed = seed
        self.encode_factor = encode_factor
        self.message = "None"
        
    def getRandColor(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return (r,g,b)
        
    def compare(self, a,b):
        if a[0] == b[0] and a[1] == b[1] and a[2] == b[2]:
            return True
        else:
            return False
    
    def split_int(self, integer, pieces):
        returnable = []
        if integer % pieces == 0:
            for i in range(pieces):
                returnable.append(int(integer/pieces))
        else:
            remainder = integer
            for i in range(pieces):
                if remainder == 0:
                    returnable.append(0)
                elif i == pieces - 1 and remainder != 0:
                    returnable.append(remainder)
                else:
                    current = int(remainder/(pieces - i))
                    if current < 1:
                        current = 1
                    returnable.append(current)
                    remainder = remainder - current
        return returnable
            
    def split_message(self, ints, factor):
        returnable = []
        for integer in ints:
            for i in self.split_int(integer, factor):
                returnable.append(i)
        return returnable
        
    def combine_message(self, ints, factor):
        i = 0
        j = 0
        temp = 0
        returnable = []
        while i < len(ints):
            temp = temp + ints[i]
            i = i + 1
            j = j + 1
            if j == factor:
                returnable.append(temp)
                temp = 0
                j = 0
        return returnable
        
    def sign(self):
        i = random.randint(0,1)
        if i == 0:
            return 1
        else:
            return -1
            
    def shift_pixel(self, pixel, amount):
        s = self.sign()
        #print("pixel:", pixel)
        if len(pixel) == 3:
            r,g,b = pixel
        else:
            r,g,b,a = pixel
        ar,ag,ab = self.split_int(amount, 3)
        if len(pixel) == 3:
            returnable = (r + (ar * s),g + (ag * s),b + (ab * s))
        else:
            returnable = (r + (ar * s),g + (ag * s),b + (ab * s), a)
        for i in range(3):
            if returnable[i] > 255 or returnable[i] < 0:
                s = s * -1
                ar,ag,ab = self.split_int(amount, 3)
                if len(pixel) == 3:
                    returnable = (r + (ar * s),g + (ag * s),b + (ab * s))
                else:
                    returnable = (r + (ar * s),g + (ag * s),b + (ab * s), a)
                for i in range(3):
                    if returnable[i] > 255 or returnable[i] < 0:
                        return None
        return returnable

    def decode_pixel(self, a, b):
        ra,ga,ba = a
        rb,gb,bb = b
        
        dr = ra - rb
        if dr < 1:
            dr = dr * -1
            
        dg = ga - gb
        if dg < 1:
            dg = dg * -1
            
        db = ba - bb
        if db < 1:
            db = db * -1
            
        return dr + dg + db
        
    def find_seed(self):
        correction = float((self.width * self.height) / (1920 * 1080))
        f = open("dict.json",'r')
        jsondict = json.load(f)
        f.close()
        done = False
        encode_factor = self.encode_factor + 1
        seed = None
        while not done:
            encode_factor = encode_factor - 1
            temp_ints = self.split_message(self.message_ints, encode_factor)
            #if self.print:
                #print("target:", len(temp_ints))
                #print("encoding_factor:",encode_factor)
            for s in jsondict.keys():
                #print(jsondict[s],s)
                num = int(int(jsondict[s]) * correction) - len(temp_ints)
                if 600 <= num and num <= 1000:
                    seed = s
                    #if self.print:
                        #print(jsondict[s],s)
                    done = True
                    break
        self.seed = seed
        self.encode_factor = encode_factor
        
    def encode_file(self, message_file):
        mf = open(message_file,'rb')
        message = mf.read()
        mf.close()
        self.encode_bytes(message)
    
    def encode_string(self, message):
        self.encode_bytes(message.encode("utf-8"))
    
    def encode_bytes(self, bytes):
        self.message_ints = []
        if self.gzip:
            bytes = zlib.compress(bytes)
        for b in base64.b64encode(bytes):
            self.message_ints.append(int(b))
            
    def points(self, delim="\n"):
        seed = Seed(self.seed)
        points = Points(self.width, self.height, seed, checkered=self.checkered, box=self.box)
        point = points.getPoint()
        c = (0,0,0)
        for y in range(self.height):
            for x in range(self.width):
                if point != None and point[0] == x and point[1] == y:
                    c = (255,0,255) 
                    point = points.getPoint()
                else:
                    c = self.input_pix[x,y]
                self.out_pix[x,y] = c
        out = "Using Seed:" + self.seed + delim
        out = out + "Total Bytes:" + str(len(points.points)) + delim
        out = out + "Available Bytes:" + str(int(len(points.points)/self.encode_factor)) + delim
        self.message = out

    def get_size(self):
        return self.input_image.size
    
    def get_message(self):
        return self.message

    def process_box(self, delim="\n"):
        try:
            points = Points(self.width, self.height, None, checkered=self.checkered, box=self.box)
            message_ints = self.split_message(self.message_ints, self.encode_factor)
            encodable_points = (self.width * self.height) - len(points.points)
            out = "Using Seed:" + self.seed + delim
            out = out + "Encoding Factor:" + str(self.encode_factor) + delim
            out = out + "Total Bytes:" + str(encodable_points) + delim
            out = out + "Used Bytes:" + str(len(message_ints)) + delim
            out = out + "Available Bytes:" + str(int(encodable_points/self.encode_factor)) + delim
            out = out + "Message Bytes:" + str(len(self.message_ints)) + delim

            if len(message_ints) > encodable_points:
                out = out + "NOT ENOUGH SPACE TO ENCODE, Try a Lower Encoding Factor or Different Seed."
                self.message = out
                return out
            if self.print:
                self.message = out
                print(out)

            message_index = 0
            d = (0,0,0)
            for i in range(len(points.points)):
                point = points.points[i]
                d = self.input_pix[point[0],point[1]]
                self.out_pix[point[0],point[1]] = d
                chunk = points.chunks[i]
                for pixel in chunk:
                    if message_index < len(message_ints):
                        c = self.shift_pixel(d, message_ints[message_index])
                        if c == None:
                            out = out + "FAILED TO ENCODE PIXEL, Try a Higher Encoding Factor."
                            self.message = out
                            return out
                        else:
                            self.out_pix[pixel[0],pixel[1]] = c
                            message_index = message_index + 1
                    else:
                        self.out_pix[pixel[0],pixel[1]] = d
            return None
        
        except Exception as e:
                print(e)
                out = "FAILED TO ENCODE PIXEL, Try a Higher Encoding Factor."
                self.message = out
                return out
        
    def process_pairs(self, delim="\n"):
        try:
            seed = Seed(self.seed)
            points = Points(self.width, self.height, seed, checkered=self.checkered, box=self.box)
            message_ints = self.split_message(self.message_ints, self.encode_factor)
            
            out = "Using Seed:" + self.seed + delim
            out = out + "Encoding Factor:" + str(self.encode_factor) + delim
            out = out + "Total Bytes:" + str(len(points.points)) + delim
            out = out + "Used Bytes:" + str(len(message_ints)) + delim
            out = out + "Available Bytes:" + str(int(len(points.points)/self.encode_factor)) + delim
            out = out + "Message Bytes:" + str(len(self.message_ints)) + delim

            if len(message_ints) > len(points.points):
                out = out + "NOT ENOUGH SPACE TO ENCODE, Try a Lower Encoding Factor or Different Seed."
                self.message = out
                return out
            if self.print:
                self.message = out
                print(out)
            message_index = 0
            point = points.getPoint()
            c = (0,0,0)
            prev = None
            for y in range(self.height):
                for x in range(self.width):
                    if point != None and point[0] == x and point[1] == y:
                        c = self.input_pix[x,y]
                        prev = c
                        point = points.getPoint()
                    elif prev != None:
                        c = prev
                        if message_index < len(message_ints):
                            c = self.shift_pixel(prev, message_ints[message_index])
                            if c == None:
                                out = out + "FAILED TO ENCODE PIXEL, Try a Higher Encoding Factor."
                                self.message = out
                                return out
                            message_index = message_index + 1
                        prev = None
                    else:
                        c = self.input_pix[x,y]
                    self.out_pix[x,y] = c
            return None
        except Exception as e:
            print(e)
            out = "FAILED TO ENCODE PIXEL, Try a Higher Encoding Factor."
            self.message = out
            return out

    def process(self, delim="\n"):
        if self.box != None:
            self.process_box(delim=delim)
        else:
            self.process_pairs(delim=delim)
    
    def decode_pairs(self):
        try:
            points = Points(self.width, self.height, Seed(self.seed), checkered=self.checkered, box=self.box)
            point = points.getPoint()
            c = (0,0,0)
            ints = []
            
            for y in range(self.height):
                for x in range(self.width):
                    if point != None and point[0] == x and point[1] == y:
                        c = self.input_pix[x,y]
                        d = self.input_pix[x + 1,y]
                        point = points.getPoint()
                        if not self.compare(c,d):
                            #print(decode_pixel(c, d).to_bytes(1, "big"))
                            ints.append(self.decode_pixel(c, d))
            #print(ints)                
            ints = self.combine_message(ints, self.encode_factor)
            decoded = b''
            for i in ints:
                decoded = decoded + i.to_bytes(1, "big")
            if self.gzip:
                self.decoded = zlib.decompress(base64.b64decode(decoded))
            else:
                self.decoded = base64.b64decode(decoded)
            return None
        except Exception as e:

            return str(e) + "\nFAILED TO DECODE!"
        
    def decode_box(self):
        try:
            points = Points(self.width, self.height, Seed(self.seed), checkered=self.checkered, box=self.box)
            c = (0,0,0)
            ints = []
            for i in range(len(points.points)):
                point = points.points[i]
                c = self.input_pix[point[0],point[1]]
                chunk = points.chunks[i]
                for pixel in chunk:
                    d = self.input_pix[pixel[0],pixel[1]]
                    if not self.compare(c,d):
                        ints.append(self.decode_pixel(c, d))

            #print(ints)                
            ints = self.combine_message(ints, self.encode_factor)
            decoded = b''
            for i in ints:
                decoded = decoded + i.to_bytes(1, "big")
            if self.gzip:
                self.decoded = zlib.decompress(base64.b64decode(decoded))
            else:
                self.decoded = base64.b64decode(decoded)
            return None
        except Exception as e:

            return str(e) + "\nFAILED TO DECODE!"
        
    def decode(self):
        if self.box != None:
            self.decode_box()
        else:
            self.decode_pairs()
    
    def get_decoded_string(self):
        return self.decoded.decode("utf-8")
        
    def get_decoded_bytes(self):
        return self.decoded
        
    def get_buffer(self):
        buf = BytesIO()
        self.out_image.save(buf, "PNG")
        buf.seek(0)
        return buf
        
    def write_file(self, outfile):
        o = open(outfile,'wb')
        o.write(self.decoded)
        o.close()    
        
    def write_image(self, outfile, tags=None):
        if tags != None:
            metadata = PngInfo()
            for key in tags:
                metadata.add_text(key, tags[key])
            self.out_image.save(outfile, pnginfo=metadata)
        else:
            self.out_image.save(outfile)
        
