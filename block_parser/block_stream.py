import stream_reader
import binascii
import os
import logging
from block import Block

#This class represents a set of files that contain the block chain.
#This starts with blk00000.dat and increments until the end of the chain.
#This class maintains a block height position within the chain.

class BlockStream:
    __current_file = 104
    __stream = None
    current_height = 0
    __at_end = False

    def __init__(self):
        self.__current_file = 104
        self.__open_file()
        
    def __open_file(self):
        try:
            if self.__stream != None:
                self.__stream.close()
            file_name = '{0}/.bitcoin/blocks/blk{1:05d}.dat'.format(os.getenv("HOME"),self.__current_file)
            self.__stream = open(file_name, 'rb')
            return True
        except IOError:
            self.__at_end = True
            return False    
    
    def advance_block(self):
        if(self.__at_end):
            return False
        magic_number = stream_reader.read_uint32(self.__stream)
        if(magic_number == None):
            if(self.__advance_file()):
                magic_number = stream_reader.read_uint32(self.__stream)
            else:
                return False
        expected_magic_number = 0xD9B4BEF9
        if (magic_number != expected_magic_number):
            self.__at_end = True
            return False
        num_bytes = stream_reader.read_uint32(self.__stream)
        self.__stream.read(num_bytes)
        self.current_height = self.current_height + 1
        return True
        
    def __advance_file(self):
        self.__current_file = self.__current_file + 1
        self.__stream.close()
        return self.__open_file()
        
    def __check_file(self):
        magic_number = self.__stream.read(4)
        if magic_number == "":
            if not self.__advance_file():
                return False
        else:
            self.__stream.seek(-4, 1)
        return True
    
    def move_to_block(self, block_height):
        if(block_height < self.current_height):
            self.__current_file = 0
            self.__open_file()
            self.__stream.seek(0)
            self.current_height = 0
        while(block_height > self.current_height):
            if (not self.advance_block()):
                return False
        return True
    
    #returns None if we are at the end of the stream
    def read_next_block(self):
        if(self.__at_end or not self.__check_file()):
            return None
        block = {}
        magic_number = stream_reader.read_uint32(self.__stream)
        expected_magic_number = 0xD9B4BEF9
        if (magic_number != expected_magic_number):
            self.__at_end = True
            return None
        block_size = stream_reader.read_uint32(self.__stream)
        self.current_height = self.current_height + 1
        return Block(stream_reader.read_data(self.__stream, block_size))
