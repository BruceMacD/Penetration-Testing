import socket

#Generic template for testing services, fuzzing, etc.

target_host = "www.google.com"
target_port = "80"

#create a socket object (IPv4 hostname, TCP client)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect the client
client.connect((target_host, target_port))

#send data
client.send("GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

#data recieve
response = client.recv(4096)

print response
