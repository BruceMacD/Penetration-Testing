#!/usr/bin/python2.7

import sys
import socket
import getopt
import threading
import subprocess

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

#provide usage instructions
def usage ():
    print "BHP Net Tool"
    print
    print "Usage: bhpnet.py -t target_host -p port"
    print "-l --listen              - listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run - execute the given file upon receiving a connection"
    print "-c --command             - initialize a command shell"
    print "-u --upload=destination  - upon receiving a connection upload a file and write to [destination]"
    print
    print
    print "Examples: "
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=C:\\target.exe"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #connect to target host
        client.connect((target,port))
        
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
        
            # send it off
            client.send(buffer)
    
    except:
        print "[*] Exception! Exiting."
        
        client.close()
        

def server_loop():
    global target
    global port
    
    #if no target, listen on all interfaces
    if not len(target):
        target = "0.0.0.0"
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()
        
        #thread to handle client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    #trim the newline
    command = command.rstrip()
    
    #run the command and get the output back
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
    except:
        output = "[-] Failed to execute command\r\n"
        
    #send the output back to the client
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command
    
    #check for upload
    if len(upload_destination):
        
        # read the bytes and write to destination
        
        file_buffer = ""
        
        #keep reading data until none is available
        while True:
            data = client_socket.recv(1024)
            
            if not data:
                break
            else:
                file_buffer += data
        
        #now write out bytes
        try: 
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            
            # acknowledge write-out
            client_socket.send("Successfully saved file to %s/r/n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s/r/n" % upload_destination)
            
    #check for command execution
    if len(execute):
        
        #run the command
        output = run_command(execute)
        
        client.socket.send(output)
        
    #command shell loop
    
    if command:
        while True:
            #show a simple prompt
            client_socket.send("<BHP:#> ")
            
            #receive until line feed
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            
            #return command output
            response = run_command(cmd_buffer)
            
            #send back the response
            client_socket.send(response)

def main():
    # needed to modify global copies of variables
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
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu",["help","listen","execute","target","port","command","upload"])
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
    if not listen and len(target) and port > 0:
            
        #read in the buffer from the commandline
        #this will block, so send CTRL-D if not sending input
            
        buffer = sys.stdin.read()
            
        print "sending data"
        #send data off
        client_sender(buffer)
            
    #wait for commands
    if listen:
        server_loop()
    
main()