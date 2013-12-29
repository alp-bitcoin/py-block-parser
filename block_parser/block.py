import stream_reader
import binascii
import os
import logging
import StringIO
from transaction import Script
import hashlib

class Block:
    
    hash_height = {}
    
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.__stream = StringIO.StringIO(raw_data)
        self.header = stream_reader.read_data(self.__stream, 80)
        header_stream = StringIO.StringIO(self.header)
        self.version = stream_reader.read_uint32(header_stream)
        self.prev_block = stream_reader.read_uint256(header_stream)
        self.hash_merckle_root = stream_reader.read_uint256(header_stream)
        self.time = stream_reader.read_uint32(header_stream)
        self.difficulty = stream_reader.read_uint32(header_stream)
        self.nonce = stream_reader.read_uint32(header_stream)
        tx_size = stream_reader.read_varint(self.__stream)
        
        if (not self.prev_block in Block.hash_height):
            self.height = 0
        else:
            self.height = Block.hash_height[self.prev_block] + 1
        Block.hash_height[self.block_hash()] = self.height 
        self.tx = []
        for tx_index in range(0, tx_size):
            self.tx.append(self.__read_transaction())

    def __read_transaction(self):
        tx = {}
        tx['version_number'] = stream_reader.read_uint32(self.__stream)
        in_counter = stream_reader.read_varint(self.__stream)
        tx['inputs'] = []
        for i in range(0, in_counter):
            tx['inputs'].append(self.__read_tx_input())
        tx['outputs'] = []
        out_counter = stream_reader.read_varint(self.__stream)
        for o in range(0, out_counter):
            tx['outputs'].append(self.__read_tx_output())
        tx['lock_time'] = stream_reader.read_uint32(self.__stream) 
        return tx

    def __read_tx_input(self):
        input = {}
        input['previous_tx_hash'] = binascii.hexlify(stream_reader.read_data(self.__stream, 32))
        input['previous_tx_out'] = stream_reader.read_uint32(self.__stream)
        script_length = stream_reader.read_varint(self.__stream)
        if script_length > 0:
            input['scriptSig'] = Script(stream_reader.read_data(self.__stream, script_length))
        else:
            logging.warn("Script Length 0!")
        input['sequence'] = stream_reader.read_uint32(self.__stream)
        return input
        

    def __read_tx_output(self):
        output = {}
        output['value'] = stream_reader.read_uint64(self.__stream)
        script_length = stream_reader.read_varint(self.__stream)
        if script_length > 0:
            output['scriptPubKey'] = Script(stream_reader.read_data(self.__stream, script_length))
        else:
            logging.warn("Script Length 0!")
            output['scriptPubKey'] = ""
        return output

    def block_hash(self):
        return hashlib.sha256(hashlib.sha256(self.header).digest()).digest()[::-1]
        
    def __str__(self):
        return "raw data: {0}\r\nversion: {1}\r\nprev_block: {2}\r\nTransactions: {3}".format(binascii.hexlify(self.__raw_data), self.version, self.prev_block, self.tx)
