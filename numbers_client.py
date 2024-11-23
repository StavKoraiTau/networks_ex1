#!/usr/bin/python3
import socket
from socket_handler import SocketHandler
import sys
import app
import re
    

def main():
    host = "localhost"
    port = 1337
    if len(sys.argv) > 3:
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
            
        

def main_loop(handler : SocketHandler) -> bool:
    while True:
        command = input()
        
        if not validate_command(command):
            if command != "quit":
                print("Invalid command format")
                command = "quit"
                
        sendall(command.encode())
        
        if command == "quit":
            return
        
        print(recvall(handler).decode())
    
def validate_command(command : str) -> bool:
    pattern = r'calculate:\s-?\d+\s[+\-*/^]\s-?\d+$|^factors:\s\d+$|^max:\s\(-?\d+(\s-?\d+)*\)$'
    return bool(re.match(pattern,command))

def auth_loop(handler: SocketHandler) -> bool:
    while True:
        username_input = input()
    
        if username_input == "quit":
            sendall(handler,app.QUIT_COMMAND.encode())
            return False
        
        if not username_input.startswith("User: "):
            print("Invalid Login Format. Remember your username prefix 'User: <username>'.")
            return False
        
        sendall(handler,username_input.encode())
        
        password_input = input()
        
        if password_input == "quit":
            sendall(handler,app.QUIT_COMMAND.encode())
            return False
            
        if not password_input.startswith("Password: "):
            print("Invalid Login Format. Remember your password prefix 'Password: <password>'.")
            return False
        
        sendall(handler,password_input.encode())
        
        response = recvall(handler).decode()
        username = username_input[len(app.USERNAME_COMMAND):]
        
        print(response) # Welcom / Login failed message
        
        if app.login_success_template(username) == response:
            return True
        
def authentication(handler : SocketHandler) -> bool:
    
    username_input = input()
    
    if username_input == "quit":
        exit(0)
        
    if not username_input.startswith("User: "):
        print("Invalid Login Format. Remember your username prefix 'User: <username>'.")
        exit(0)
        
    password_input = input()
    
    if password_input == "quit":
        exit(0)
        
    if not password_input.startswith("Password: "):
        print("Invalid Login Format. Remember your password prefix 'Password: <password>'.")
        exit(0)
        
    
    handler.set_write(username_input.encode())
    try:
        while handler.writing():
            handler.write()
        handler.set_write(password_input.encode())
        while handler.writing():
            handler.write()
    except OSError:
        print("Error writing to server")
    try:
        handler.set_read()
        while handler.reading():
            handler.read()
        response = handler.get_msg().decode()
        username = username_input[len(app.USERNAME_COMMAND):]
        
        print(response) # Welcome message.
        
        if app.login_success_template(username) == response:
            return True
        else:
            return False
        
    except OSError:
        print("Error writing to server")
        
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
    