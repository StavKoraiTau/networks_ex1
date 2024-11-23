#!/usr/bin/python3
import socket
from socket_handler import SocketHandler
import sys
import app
import re

def main():
    host = "localhost"
    port = 1337
    if len(sys.argv) != 3 and len(sys.argv) != 1:
        print("Invalid number of arguments, expected ./numbers_client.py [hostname [port]]")
        return
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) == 3:
        try:
            port = int(sys.argv[2])
        except:
            print("Invalid port number")
    run_app_connection(host, port)
    

def run_app_connection(host : str, port : int) -> None:
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host,port))
        except OSError:
            print(f"Error connecting to host : {host} on port {port}")
            return
        try:
            handler = SocketHandler(sock)
            print(recvall(handler).decode())
            
            if not auth_loop(handler):
                return
            
            main_loop(handler)

        except OSError:
            print("Error with connection to server.")
        except BrokenPipeError:
            print("Error with connection to server.")
            
        

def main_loop(handler : SocketHandler) -> bool:
    while True:
        command = input()
        
        if not validate_command(command):
            if command != "quit":
                print("Invalid command format")
                command = "quit"
                
        sendall(handler, command.encode())
        
        if command == "quit":
            return
        
        print(recvall(handler).decode())
    
def validate_command(command : str) -> bool:
    pattern = r'(calculate:\s-?\d+\s[+\-*/^]\s-?\d+|^factors:\s-?\d+|^max:\s\(-?\d+(\s-?\d+)*\))$'
    return bool(re.match(pattern,command))

def auth_loop(handler: SocketHandler) -> bool:
    while True:
        username_input = input()
    
        if username_input == app.QUIT_COMMAND:
            sendall(handler, app.QUIT_COMMAND.encode())
            return False
        
        if not username_input.startswith(app.USERNAME_COMMAND):
            print("Invalid Login Format. Remember your username prefix 'User: <username>'.")
            sendall(handler, app.QUIT_COMMAND.encode())
            return False
        
        sendall(handler, username_input.encode())
        
        password_input = input()
        
        if password_input == app.QUIT_COMMAND:
            sendall(handler, app.QUIT_COMMAND.encode())
            return False
            
        if not password_input.startswith(app.PASSWORD_COMMAND):
            print("Invalid Login Format. Remember your password prefix 'Password: <password>'.")
            sendall(handler, app.QUIT_COMMAND.encode())
            return False
        
        sendall(handler, password_input.encode())
        
        response = recvall(handler).decode()
        username = username_input[len(app.USERNAME_COMMAND):]
        
        print(response) # Welcom / Login failed message
        
        if app.login_success_template(username) == response:
            return True
        
        
def sendall(handler : SocketHandler, msg : bytes) -> None:
    handler.set_write(msg)
    while handler.writing():
        handler.write()
        
def recvall(handler : SocketHandler) -> bytes:
    handler.set_read()
    while handler.reading():
        handler.read()
    return handler.get_msg()

if __name__ == "__main__":
    main()
    