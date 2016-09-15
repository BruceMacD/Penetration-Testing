#!/usr/bin/python
import socket

#TCP client modified for UDP
target_host = "127.0.0.1"
target_port = 9999

#create a socket object (IPv4 hostname, TCP client)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#send data, no need to connect UDP
client.sendto("Hello from UDP", (target_host,target_port))

#data recieved
data, addr = client.recv(4096)

print data
