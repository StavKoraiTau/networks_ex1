

import socket
from enum import Enum
import protocol

class HandlerMode(Enum):
    HEADER_READ = 0
    READ = 1
    WRITE = 2
    
class SocketHandler:
    def __init__(self,soc : socket.socket) -> None:
        self._msg : bytes
        self._socket = soc
        self._msg_bytes_done = 0
        self._msg_byte_len = 0
        self._mode = HandlerMode.WRITE
        
    def read(self) -> None:
        if self.bytes_left() <= 0:
            return
        self._msg += self._socket.recv(self.bytes_left())
        self._msg_bytes_done = len(self._msg)
        if self._mode == HandlerMode.HEADER_READ and self.done_with_msg():
            full_length = protocol.decode_header(self._msg)
            self._msg_byte_len = full_length
            self._mode = HandlerMode.READ
        
    def write(self) -> None:
        self._msg_bytes_done += self._socket.send(self._msg[self._msg_bytes_done:])
        
    def bytes_left(self) -> int:
        return self._msg_byte_len - self._msg_bytes_done
    
    def done_with_msg(self) -> bool:
        return self.bytes_left() == 0
    
    def get_msg(self) -> bytes:
        if not self.done_with_msg():
            raise Exception("Trying to get msg before finished fully reading")
        return self._msg[protocol.HEADER_LEN:]
    
    def set_read(self) -> None:
        self._mode = HandlerMode.HEADER_READ
        self._msg_byte_len = protocol.HEADER_LEN
        self._msg_bytes_done = 0
        self._msg = bytes()
        
        
    def set_write(self, msg : bytes) -> None:
        self._mode = HandlerMode.WRITE
        self._msg_bytes_done = 0
        self._msg = protocol.encode_message(msg)
        self._msg_byte_len = len(self._msg)
        
    def reading(self) -> bool:
        if not self.done_with_msg():
            return self._mode == HandlerMode.HEADER_READ or self._mode == HandlerMode.READ
        return False
    
    def writing(self) -> bool:
        if not self.done_with_msg():
            return self._mode == HandlerMode.WRITE
        return False
    
    
    def get_socket(self) -> socket.socket:
        return self._socket
        
    def close(self) -> None:
        self._socket.close()
        
        