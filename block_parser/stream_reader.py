import struct
import logging
import binascii

def read_data(stream, bytes):
    return stream.read(bytes)

def __read_number(stream, bytes):
    if(bytes == 1):
        code = "B"
    elif(bytes == 2):
        code = "H"
    elif(bytes == 4):
        code = "I"
    elif(bytes == 8):
        code = "Q"
    else:
        raise Exception()
    val = stream.read(bytes)
    if(len(val) != bytes):
        return None
    return struct.unpack("<{0}".format(code), val)[0]

def read_uint8(stream):
    return __read_number(stream, 1)

def read_uint16(stream):
    return __read_number(stream, 2)

def read_uint32(stream):
    return __read_number(stream, 4)

def read_uint64(stream):
    return __read_number(stream, 8)

def read_uint256(stream):
    return stream.read(32)[::-1]

def read_varint(stream):
    byte = read_uint8(stream)
    if (byte < 0xfd):
        return byte
    elif(byte == 0xfd):
        return read_uint16(stream)
    elif(byte == 0xfe):
        return read_uint36(stream)
    elif(byte == 0xff):
        return read_uint64(stream)
