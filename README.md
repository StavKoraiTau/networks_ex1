# networks_ex1

## numbers_client
Handles client connection to server, some input validation is done to check  
if commands are in the right format but the semantic validation is done on the server.

## numbers_server
Handles connections to all clients and manages the app instances, multiplexes between the clients with none blocking reads and write using the select module and SocketHandler class.

## socket_handler
Implements an interface to incremently read or write messages.

## app
implements all the app side logic and the data of the protocol messages.

## protocol
Helper functions to wrap messages with the protocol header.
