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
                
                data     = client.recv(4096)
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
        
def server_loop():
    global target
    
    #if no target, listen on all interfaces
    if not len(target):
        target = "0.0.0.0"
        
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()
        
        #thread to handle new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    #trim new line
    command = command.rstrip()
    
    #run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute the command. \r\n"
        
    #send the output back to the client
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command
    
    #check for upload
    if len(upload_destination):
        
        #read the bytes to werite to the destination    
        file_buffer = ""
        
        #keep reading data until none is avaliable
        while True:
            data = client_socket.recv(1024)
            
            if not data:
                break
            else:
                file_buffer += data
                
        #now write out bytes
            try:
                file_descriptor = open(upload_destination, "wb")
                file_descriptor.write(file_buffer)
                file_desciptor.close()
                
                #acknowledge write-out
                client_socket.send("Successfully saved the file to %s\r\n" % upload_destination)
            except:
                client_socket.send("Failed to save the file to %s\r\n" % upload_destination)
    
    #check cmd execution    
    if len(execute):
        
        #run the command
        output = run_command(execute)
        
        client_socket.send(output)
        
    #command shell loop
    if command:
        
        while True:
            #show a simple prompt
            client_socket.send("<BHP:#>")
            
            #receive until line feed
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
                
            #return cmd output
            response = run_command(cmd_buffer)
            
            #send back the response
            client_socket.send(respose)