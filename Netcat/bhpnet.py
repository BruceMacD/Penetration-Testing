#!/usr/bin/python
import sys
import socket
import getopt
import threading
import subprocess

listen             = False
command            = False
upload             = False
execute            = ""
target             = ""
upload_destination = ""
port               = 0

#provide usage instructions
def usage():
    print "BHP Net Tool"
    print
    print "Usage: bhpnet.py -t target_host -p port"
    print "-l --listen - listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run - execute the given file upon reciving a connection"
    print "-c --command - init command shell"
    print "-u --upload==destination - upload and write to a file to [destination] upon a connection"
    print
    print
    print "Examples: "
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGH' | ./bhpnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)
    
def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    
    #catch empty input
    if not len(sys.argv[1:]):
        usage()
    
    #read commands
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        
    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
            
        #check listen or send data from stdin
        #mimics netcat
        if not listen and len(target) and port > 0:
            #read buffer from cmd line
            #CTRL+D to bypass stdin read if no data
            buff = sys.stfin.read()
            
            client_sender(buffer)
            
        if listen:
            #wait for commands
            server_loop()
            
main()

def client_sender(buffer):
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        #connect to target host
        client.connect((target, port))
        
        if len(buffer):
            client.send(buffer)
            
        while True:
            
            #wait for data back
            recv_len = 1
            response = ""
            
            while recv_len:
                
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                
                if recv_len < 4096:
                    break
                
            print response,
            
            #wait for additional input
            buffer = raw_input("")
            buffer += "\n"
            
            #send it off
            client.send(buffer)
            
    except:
        
        print "[*] Exception. Exiting"
        
        client.close()

#TODO: add features
            
            
            
            
        