import datetime
import MySQLdb
import binascii

def publish_blocks(conn, cursor, block_stream, num_blocks):
    inserts = []
    for i in range (0, num_blocks):
        block = block_stream.read_next_block()
        inserts.append("('{0}', '{1}', {2}, FROM_UNIXTIME({3}))".format(binascii.hexlify(block.block_hash()), binascii.hexlify(block.prev_block), block.height, block.time))
    print ", ".join(inserts)
    cursor.execute("INSERT INTO blocks (block_hash, previous_hash, height, timestamp) VALUES {0}".format(", ".join(inserts)))
    
    conn.commit()
