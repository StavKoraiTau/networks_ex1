#!/usr/bin/python3
import socket
from socket_handler import SocketHandler
def main():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
        sock.connect(("localhost",1337))
        handler = SocketHandler(sock)
        while True:
            cmd = input()
            if cmd == "r":
                handler.set_read()
                while handler.reading():
                    handler.read()
                print(handler.get_msg().decode())
            elif cmd == "w":
                msg = input()
                handler.set_write(msg.encode())
                handler.write()
                if msg == "quit":
                    break
    




if __name__ == "__main__":
    main()