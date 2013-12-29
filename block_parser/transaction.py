import logging
import binascii
import stream_reader
import StringIO
import hashlib

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

def pub_key_to_addr(pubkey):
    h = hashlib.new('ripemd160')
    
    h.update(hashlib.sha256(binascii.unhexlify(pubkey)).digest())
    step1 = "00" + h.hexdigest()
    checksum = hashlib.sha256(hashlib.sha256(binascii.unhexlify(step1)).digest()).hexdigest()[0:8]
    address = step1 + checksum
    return __convert_to_base58(address)

def __convert_to_base58(value):
    long_value = 0
    for (i, c) in enumerate(binascii.unhexlify(value)[::-1]):
        long_value += (256**i) * ord(c)
     
    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div
    result = __b58chars[long_value] + result
     
    nPad = 0
    for c in binascii.unhexlify(value):
        if c == '\0': nPad += 1
        else: break
    return (__b58chars[0]*nPad) + result
        


class OpCode(int):
    OP_0 = 0x00
    OP_CHECKSIG = 0xac
    OP_DUP = 0x76
    OP_HASH160 = 0xa9
    OP_EQUALVERIFY = 0x88
    

    def __str__(self):
        if self == OpCode.OP_0:
            return "OP_0"
        elif self == OpCode.OP_CHECKSIG:
            return "OP_CHECKSIG"
        elif self == OpCode.OP_DUP:
            return "OP_DUP"
        elif self == OpCode.OP_HASH160:
            return "OP_HASH160"
        elif self == OpCode.OP_EQUALVERIFY:
            return "OP_EQUALVERIFY"
        else:
            return int.__str__(self)


class ScriptData:
    def __init__(self, data):
        self.__data = data
        
    def __str__(self):
        return binascii.hexlify(self.__data)

class Script:
    
    def __init__(self, script_data):
        self.__op_codes = []
        script_data = StringIO.StringIO(script_data)
        next_byte = stream_reader.read_uint8(script_data)
        while(next_byte != None):
            self.__op_codes.append(OpCode(next_byte))
            if next_byte >=0x01 and next_byte <=0x4B:
                self.__op_codes.append(ScriptData(script_data.read(next_byte)))
            next_byte = stream_reader.read_uint8(script_data)
    
    def __str__(self):
        return "Script: [{0}]".format(" ".join(['{0}'.format(element) for element in self.__op_codes]))
        
    def payment_address(self):
        if self.pays_to_address():
            return self.__op_codes[3]
        elif self.pays_to_pubkey():
            return pub_key_to_addr(str(self.__op_codes[1]))
        else:
            return None
    
    def pays_to_pubkey(self):
        if (len(self.__op_codes) == 3):
            return self.__op_codes[0] == 65 and self.__op_codes[2] == OpCode.OP_CHECKSIG
            
    def pays_to_address(self):
        if (len(self.__op_codes) == 6):
            return self.__op_codes[0] ==OpCode.OP_DUP and self.__op_codes[1] == OpCode.OP_HASH160 and self.__op_codes[2] == 20 and self.__op_codes[4] == OpCode.OP_EQUALVERIFY and self.__op_codes[5] == OpCode.OP_CHECKSIG
