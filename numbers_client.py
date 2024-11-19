#!/usr/bin/python3
import socket
from socket_handler import SocketHandler
import sys
import app
import re
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
                while handler.writing():
                    handler.write()
                if msg == "quit":
                    break
    

def main2():
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
        handler = SocketHandler(sock)
        handler.set_read()
        while handler.reading():
            handler.read()
        print(handler.get_msg().decode())
        authentication_template = "User: <username>\nPassword: <password>"
        print(f"Enter username and password in the format \n {authentication_template}")
        while not authentication(handler):
            pass
        while main_loop(handler):
            pass

def main_loop(handler : SocketHandler) -> bool:

    command = input("Enter command for server")
    if not validate_command(command):
        print("Invalid command format")
        command = "quit"
    handler.set_write(command.encode())
    try:
        while handler.writing():
            handler.write()
    except OSError:
        print("Error writing to server.")
        return False
    if command == "quit":
        return False
    handler.set_read()  
    try:
        while handler.reading():
            handler.read()
    except OSError:
        print("Error reading from server.")
    print(handler.get_msg())
    return True
    
def validate_command(command : str) -> bool:
    pattern = r'calculate:\s-?\d+\s[+\-*/]\s-?\d+$|^factors:\s\d+$|^max:\s\(-?\d+(\s-?\d+)*\)$'
    return bool(re.match(pattern,command))

def authentication(handler : SocketHandler) -> bool:
    username_input = input()
    password_input = input()
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
        print(response)
        if app.login_success_template(username) == response:
            return True
        else:
            return False
        
    except OSError:
        print("Error writing to server")

if __name__ == "__main__":
    main2()