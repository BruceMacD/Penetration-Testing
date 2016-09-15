#!/usr/bin/python
import socket
import threading

#Multithreaded TCP Server

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

#set connection backlog
server.listen(5)

print "[*] Listening on %s:%d" %(bind_ip, bind_port)

#handle clients
def handle_client(client_socket):
    
    #print recieved
    request = client_socket.recv(1024)
    print "[*] Received: %s" % request
    
    #send a packet back
    client_socket.send("Request recieved")
    client_socket.close()
    
while True:
    client, addr = server.accept()
    print "[*] Accepted condition from: %s:%d" % (addr[0], addr[1])
    
    #handle incoming data on client thread
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()