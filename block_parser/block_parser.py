import stream_reader
import binascii
import os
import logging
import StringIO

class Block:
    
    def __init__(self, raw_data):
        self.__raw_data = raw_data
        self.__stream = StringIO.StringIO(raw_data)
        self.version = stream_reader.read_uint32(self.__stream)
        self.prev_block = binascii.hexlify(stream_reader.read_data(self.__stream, 32))
        self.hash_merckle_root = binascii.hexlify(self.__stream.read(32))
        self.time = stream_reader.read_uint32(self.__stream)
        self.difficulty = stream_reader.read_uint32(self.__stream)
        self.nonce = stream_reader.read_uint32(self.__stream)
        tx_size = stream_reader.read_varint(self.__stream)
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
        input['previous_tx_hash'] = binascii.hexlify(self.__stream.read(32))
        input['previous_tx_out'] = stream_reader.read_uint32(self.__stream)
        script_length = stream_reader.read_varint(self.__stream)
        if script_length > 0:
            input['scriptSig'] = binascii.hexlify(self.__stream.read(script_length))
        else:
            input['scriptSig'] = ""
        input['sequence'] = stream_reader.read_uint32(self.__stream)
        return input
        

    def __read_tx_output(self):
        output = {}
        output['value'] = stream_reader.read_uint64(self.__stream)
        script_length = stream_reader.read_varint(self.__stream)
        if script_length > 0:
            output['scriptPubKey'] = binascii.hexlify(self.__stream.read(script_length))
        else:
            output['scriptPubKey'] = ""
        return output

    def __str__(self):
        return "raw data: {0}\r\nversion: {1}\r\nprev_block: {2}\r\nTransactions: {3}".format(binascii.hexlify(self.__raw_data), self.version, self.prev_block, self.tx)
