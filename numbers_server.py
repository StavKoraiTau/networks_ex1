#!/usr/bin/python3

import socket_handler

import select
import struct
import socket
class state:
    def __init__(self) -> None:
        self._count = 0 # num of bytes read
        welcome_msg = b"Welcome, please log in."
        self._length = struct.calcsize("!I")+len(welcome_msg)
        self._msg = struct.pack("!I",self._length).join(welcome_msg)
        self._mode = "write" # read/write/header_read
    def get_next(self) -> bytes:
        return self._msg[self._count:]
    def remaining_bytes(self) -> int:
        return self._length - self._count
    def get_mode(self) -> str:
        return self._mode
    def inc_count(self, cnt : int) -> None:
        self._count += cnt
    def append(self, buff : bytes)-> None:
        self._msg.join(buff)
    def set_mode(self,mode : str):
        self._mode = mode
        
if __name__ == "__main__":
    port = 1337
    clients_sockets : dict[socket.socket,state] = {}
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server_socket:
        server_socket.bind("", port)
        server_socket.listen(10)
        print("Started listening")
        
        while True:
            readable, writeable, _ = select.select([
                sock for sock,state in clients_sockets if state.get_mode() in ["read","read_header"]
            ] + [server_socket],
            [
                sock for sock,state in clients_sockets if state.get_mode() == "write"
            ],
            []
            )
            
            for sock in readable:
                if sock == server_socket:
                    acc_sock, addr = server_socket.accept()
                    clients_sockets[acc_sock] = state()
                else:
                    sock_state = clients_sockets[sock]
                    buff = sock.recv(sock_state.remaining_bytes())
                    sock_state.inc_count(len(buff))
                    sock_state.append(buff)
                    if sock_state.remaining_bytes() == 0:
                        #process
                        if sock_state.get_mode() == "read_header":
                            sock_state.set_mode("read")
                            sock_state._count = 0
                            sock_state._length = struct.unpack("!I",sock_state._msg)
                        else:
                            #parse - need to parse different commands
                            print(sock_state._msg)
                            sock_state.set_mode("write")
                            pass
                for sock in writeable:
                    pass #send msg saved in state
                        
                            
                            
                        
                    
                    
            
            
    
    pass