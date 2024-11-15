#!/usr/bin/python3
import socket
import app
import socket_handler
import select
from app import NextAction
def main():
    auth_db = load_db("database.txt")
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as listen_sock:
        listen_sock.bind(("",1337))
        listen_sock.listen(100)
        apps : dict[socket.socket,tuple[socket_handler.SocketHandler,app.AppInstance]]= {}
        while True:
            print(len(apps))
            readables, writeables, _ = select.select(
                [sock for sock,handler_app in apps.items() if handler_app[0].reading()] + 
                [listen_sock],
                [sock for sock,handler_app in apps.items() if handler_app[0].writing()],
                [], 0.1
            )
            if listen_sock in readables:
                sock, _ = listen_sock.accept()
                handler = socket_handler.SocketHandler(sock)
                app_inst = app.AppInstance(auth_db)
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
                if not handler.done_with_msg():
                    continue
                next_action(apps,handler,app_inst, handler.get_msg())
            
            for sock in writeables:
                handler, app_inst = apps[sock]
                try:
                    handler.write()
                except OSError:
                    sock.close()
                    apps.pop(sock)
                if not handler.done_with_msg():
                    continue
                next_action(apps,handler,app_inst)

def next_action(apps : dict, handler : socket_handler.SocketHandler,
            app_inst : app.AppInstance, message : bytes | None = None):
    next_act, opt_msg = app_inst.next(message)
    if next_act == NextAction.QUIT:
        apps.pop(handler.get_socket())
        handler.close()
    elif next_act == NextAction.SEND:
        handler.set_write(opt_msg)
    elif next_act == NextAction.RECV:
        handler.set_read()
    
def load_db(file_path : str) -> dict[str,str]:
    with open(file_path, "r") as f:
        entries = [l[:len(l)-1].split("\t") for l in f.readlines() if l]
        database = {u:p for u,p in entries}
    return database

if __name__ == "__main__":
    main()