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


def proxy_handler(client_socket, remote_host, remote_port, receive_first):

    # connect to remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:

        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        remote_buffer = response_handler(remote_buffer)

        # send data if exists
        if len(remote_buffer):
            print ("## Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)

        # read local, send remote loop
        while True:
            local_buffer = receive_from(client_socket)

            if len(local_buffer):
                print ("## Received %d bytes from localhost" % len(local_buffer))
                hexdump(local_buffer)

                # send
                local_buffer = request_handler(local_buffer)
                remote_socket.send(local_buffer)
                print("## Sent to remote")

            # response
            remote_buffer = receive_from(remote_socket)

            if len(remote_buffer):
                print ("## Received %d bytes from remote" % len(remote_buffer))
                hexdump(remote_buffer)

                # send to response
                remote_buffer = response_handler(remote_buffer)
                client_socket.send(remote_buffer)
                print("## Sent to localhost")

            # check to close connection when no more data is being sent
            if not len(local_buffer) or not len(remote_buffer):
                client_socket.close()
                remote_socket.close()
                print("Connection closed")

                break


# hexdumper from http://code.activestate.com/recipes/142812-hex-dumper/
def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
        s = src[i:i + length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X   %-*s   %s" % (i, length * (digits + 1), hexa, text))
    return b'\n'.join(result)


def receive_from(connection):
    buffer = ""
    connection.settimeout(2)

    try:
        # read buffer until no more data or time up
        while True:
            data = connection.recv(4096)

            if not data:
                break
            buffer += data
    except:
        pass

    return buffer


def request_handler(buffer):
    # return modified packets for local host
    return  buffer


def response_handler(buffer):
    # return modified packets for remote host
    return buffer


def main():

    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [recive_first]")
        print("Ex: ./proxy.py 127.0.0.1 9000 10.12.123.1 9000 True")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # target
    remote_host = sys.srgv[3]
    remote_port = int(sys.argv[2])

    # connect proxy before sending
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    # spin up on listening socket
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

main()