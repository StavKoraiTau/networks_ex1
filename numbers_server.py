#!/usr/bin/python3
import socket
import app
import socket_handler
import select
import sys
from app import NextAction
import csv
def main():
    port = 1337
    db_file_path = ""
    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print("Invalid number of argument, expected ./numbers_server.py users_file [port]")
        print(f"len={len(sys.argv)} args={[arg for arg in sys.argv]}")
        return
    if len(sys.argv) == 3:
        try:
            port = int(sys.argv[2])
        except:
            print(sys.argv[2])
            print("Invalid value for port argument.")
            return
    db_file_path = sys.argv[1]
    try:
        auth_db = load_db(db_file_path)
    except:
        print("Error reading username database.")
        return
    server_loop(auth_db, port)

                
def server_loop(auth_db : dict[str,str], port : int) -> None:
    """startup listening, accepting clients and managing the communication between the app
    instances and the sockets

    Args:
        auth_db (dict[str,str]): a dictionary of usernames:passwords
        port (int): 
    """
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as listen_sock:
        listen_sock.bind(("",port))
        
        listen_sock.listen(1000)
        apps : dict[socket.socket,tuple[socket_handler.SocketHandler,app.ServerAppInstance]]= {}
        
        while True:
            readables, writeables, _ = select.select(
                [sock for sock,handler_app in apps.items() if handler_app[0].reading()] + 
                [listen_sock],
                [sock for sock,handler_app in apps.items() if handler_app[0].writing()],
                [], 0.1
            )
            
            if listen_sock in readables:
                sock, _ = listen_sock.accept()
                handler = socket_handler.SocketHandler(sock)
                app_inst = app.ServerAppInstance(auth_db)
                apps[sock] = (handler,app_inst)
                next_action(apps,handler,app_inst)
                readables.remove(listen_sock)

            for sock in readables:
                handler, app_inst = apps[sock]
                try:
                    handler.read()
                except OSError:
                    sock.close()
                    apps.pop(sock)
                if handler.done_with_msg():
                    next_action(apps,handler,app_inst, handler.get_msg())
                
            for sock in writeables:
                
                handler, app_inst = apps[sock]
                try:
                    handler.write()
                except OSError:
                    sock.close()
                    apps.pop(sock)
                if handler.done_with_msg():
                    next_action(apps,handler,app_inst)
                    
def next_action(apps : dict, handler : socket_handler.SocketHandler,
            app_inst : app.ServerAppInstance, message : bytes | None = None) -> None:
    next_act, opt_msg = app_inst.next(message)
    if next_act == NextAction.QUIT:
        apps.pop(handler.get_socket())
        handler.close()
    elif next_act == NextAction.SEND:
        handler.set_write(opt_msg)
    elif next_act == NextAction.RECV:
        handler.set_read()
    
def load_db(file_path : str) -> dict[str,str]:
    with open(file_path, "r", newline="") as f:
        csv_reader = csv.reader(f,delimiter="\t")
        database = {u:p for u,p in csv_reader}
    return database

if __name__ == "__main__":
    main()