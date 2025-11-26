import serial
from enum import IntEnum, auto
import time    

class Cmds(IntEnum):
    PUMP= 1
    DISC= 2
    BTN= 3
    SOLENOID= 4

#This class wont have its own thread, so the main loop will have to call get_msg
 
class Communicator:
    def __init__(self, port, timeout=3):
        self._sr = serial.Serial(port, 115200)
        self.timeout = timeout
        
    def message_available (self):
        return self._sr.in_waiting > 0
    
    def get_msg(self, with_ack = False):
        if not self.message_available(): return None;
        byte = self._sr.read()[0]
        
        msg = self.__decode_msg(byte)
        #is_ack is for the use of this class only
        if not with_ack:
            del msg['is_ack']
            
        return msg;

    def send_msg(self, cmd, param):
        #get the msg byte
        byte = self.__encode_msg(cmd, param)
        
        attempts = 0;
        ack = False;
        
        #wait for the ack
        while attempts < 3 and not ack:
            req_start = time.perf_counter()
            
            #send the msg    
            self._sr.write(bytes([byte]))
            
            #wait for a response until the timeout
            while time.perf_counter() - req_start < self.timeout:
                
                if(self.message_available()):
                    res_byte = self._sr.read()[0]
                 
                    is_ack = (res_byte >> 7) & 0b1
                    
                    #I got a message back but it is not an acknowledgment?? should not happen but still
                    if not is_ack:
                        break
                    
                    #set the ack bit to 0 and test against the original sent byte
                    if(res_byte ^ (1<<7) == byte):
                        ack = True
                        break
                    
            if not ack: attempts += 1
        return ack
    
    @staticmethod
    def __encode_msg(cmd, val):
        #arduino doesn't care about the python ack because python is the initiator
        msg = 0
        msg |= (cmd & 0b111) << 4
        msg |= (val & 0b1111)
        
        return msg;
    
    @staticmethod
    def __decode_msg(byte):
        decoded = {
            "is_ack": (byte >> 7) & 0b1,
            "cmd": Cmds((byte >> 4) & 0b111).name,
            "val": byte & 0b1111
        }
        return decoded;
    
        
        