

import socket
from enum import Enum
import protocol
"""
Implements a class to handle the reading and writing of messages given in 
bytes using the protocol (headers). Used to incremently reading or writing the messages
useful when multiplexing different clients.
"""
    
class HandlerMode(Enum):
    HEADER_READ = 0
    READ = 1
    WRITE = 2
    
class SocketHandler:
    def __init__(self,soc):
        self._msg : bytes
        self._socket = soc
        self._msg_bytes_done = 0
        self._msg_byte_len = 0
        self._mode = HandlerMode.WRITE
        
    def read(self):
        """reads up to expected number of bytes of the current message, if on header will only read
        first 4 bytes to determine length of the rest of the message and the continue to read the rest.
        """
        if self.bytes_left() <= 0:
            return
        self._msg += self._socket.recv(self.bytes_left())
        self._msg_bytes_done = len(self._msg)
        if self._mode == HandlerMode.HEADER_READ and self.done_with_msg():
            full_length = protocol.decode_header(self._msg)
            self._msg_byte_len = full_length
            self._mode = HandlerMode.READ
        
    def write(self):
        """writes up to the remaining bytes left in the message
        """
        self._msg_bytes_done += self._socket.send(self._msg[self._msg_bytes_done:])
        
    def bytes_left(self):
        """bytes left in the current message (or header of the message)

        Returns:
            int: bytes left
        """
        return self._msg_byte_len - self._msg_bytes_done
    
    def done_with_msg(self):
        return self.bytes_left() == 0
    
    def get_msg(self):
        if not self.done_with_msg():
            raise Exception("Trying to get msg before finished fully reading")
        return self._msg[protocol.HEADER_LEN:]
    
    def set_read(self):
        """set the handler to start reading a message and subsequent reads will fill the message
        """
        self._mode = HandlerMode.HEADER_READ
        self._msg_byte_len = protocol.HEADER_LEN
        self._msg_bytes_done = 0
        self._msg = bytes()
        
        
    def set_write(self, msg):
        """set a message to write, subsequent writes will write the message until done

        Args:
            msg (bytes): _description_
        """
        self._mode = HandlerMode.WRITE
        self._msg_bytes_done = 0
        self._msg = protocol.encode_message(msg)
        self._msg_byte_len = len(self._msg)
        
    def reading(self):
        if not self.done_with_msg():
            return self._mode == HandlerMode.HEADER_READ or self._mode == HandlerMode.READ
        return False
    
    def writing(self):
        if not self.done_with_msg():
            return self._mode == HandlerMode.WRITE
        return False
    
    
    def get_socket(self):
        return self._socket
        
    def close(self):
        self._socket.close()
        
        