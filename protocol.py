import struct
BYTE_ORDER = "!"
HEADER_FORMAT = BYTE_ORDER + "I"
HEADER_LEN = struct.calcsize(HEADER_FORMAT)

def encode_header(msg_length):
    return struct.pack(HEADER_FORMAT, msg_length)

def decode_header(header):
    length, = struct.unpack(HEADER_FORMAT, header)
    return length

def decode_message(encoded_msg):
    length = decode_header(encoded_msg[:HEADER_LEN])
    return encoded_msg[HEADER_LEN:length]

def encode_message(msg):
    return encode_header(HEADER_LEN + len(msg)) + msg


