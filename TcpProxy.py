import sys
import socket
import threading


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except:
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        # local connection information
        print("[==>] Received incoming connection from %s:%d" % (addr[0], addr[1]))
        # start a thread to connect to remote host
        proxy_thread = threading.Thread(target=proxy_handler,
                                        args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():

    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [recive_first]")
        print("Ex: ./proxy.py 127.0.0.1 9000 10.12.123.1 9000 True")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    #target
    remote_host = sys.srgv[3]
    remote_port = int(sys.argv[2])

    #connect proxy before sending
    receive_first = sys.argv[5]

    if "True" in receive_first:
        recieve_first = True
    else:
        recieve_first =False

    #spin up on listening socket
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

main()