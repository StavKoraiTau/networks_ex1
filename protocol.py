import struct
BYTE_ORDER = "!"
HEADER_FORMAT = BYTE_ORDER + "I"
HEADER_LEN = struct.calcsize(HEADER_FORMAT)

def encode_header(msg_length : int) -> bytes:
    return struct.pack(HEADER_FORMAT, msg_length)

def decode_header(header : bytes) -> int :
    length, = struct.unpack(HEADER_FORMAT, header)
    return length

def decode_message(encoded_msg : bytes) -> bytes:
    length = decode_header(encoded_msg[:HEADER_LEN])
    return encoded_msg[HEADER_LEN:length]

def encode_message(msg : bytes) -> bytes:
    return encode_header(HEADER_LEN + len(msg)) + msg


