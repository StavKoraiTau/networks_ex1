#!/usr/bin/python3

import socket_handler

import select
import struct
class state:
    def __init__(self) -> None:
        self._count = 0 # num of bytes read
        welcome_msg = b"Welcome, please log in."
        self._length = struct.calcsize("!I")+len(welcome_msg)
        self._msg = struct.pack("!I",self._length).join(welcome_msg)
        self._mode = "write" # read/write
    def get_next(self) -> bytes:
        return self._msg[self._count:]
    def inc_count(self, cnt : int) -> None:
        self._count += cnt
if __name__ == "__main__":
        
    pass