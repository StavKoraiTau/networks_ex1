import struct
BYTE_ORDER = "!"
HEADER_FORMAT = BYTE_ORDER + "I"
HEADER_LEN = struct.calcsize(HEADER_FORMAT)

def encode_header(msg_length : int) -> bytes:
    return struct.pack(HEADER_FORMAT, msg_length)

def decode_header(header : bytes) -> int :
    length, = struct.unpack(HEADER_FORMAT, header)
    return length

def encode_message(msg : bytes) -> bytes:
    return encode_header(len(msg))+ msg

def decode_message(encoded_msg : bytes) -> bytes:
    length = decode_header(encoded_msg[:HEADER_LEN])
    return encoded_msg[HEADER_LEN:length]

def decode_ints(encoded_ints : bytes) -> list[int]:
    return list(struct.iter_unpack(BYTE_ORDER+"I", encoded_ints))

def encode_ints(ints : list[int]) -> bytes:
    return struct.pack(BYTE_ORDER+(f"{len(ints)}I"), *ints)

def encode_message(msg : bytes) -> bytes:
    return encode_header(HEADER_LEN + len(msg)) + msg


