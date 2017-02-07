import socket
import os
import time
import threading

from netaddr import IPNetwork, IPAddress
from ctypes import *

# listen on
host = "192.168.0.196"

# subnet to target
subnet = "192.168.0.0/24"

# string to check responses for
message = "response from original"


# this sprays out the UDP datagram
def udp_sender(subnet, message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DIAGRAM)

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(message, ("%s" % ip, 65212))
        except:
            pass


# ip header
class IP(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_ulong),
        ("dst", c_ulong)
    ]

    def _new_(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):

        # protocol names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # readable IP address
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


class ICMP(Structure):
    _fields_ = [
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("checksum", c_ushort),
        ("unused", c_ushort),
        ("next_hop_mtu", c_ushort)
        ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass

# create raw socket and bind it to the public interface
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))

# include IP headers in capture
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# setup promiscuous in Windows
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# start sending packets
t = threading.Thread(target=udp_sender, args=(subnet, message))
t.start()

try:

    while True:

        # read packet
        raw_buffer = sniffer.recvfrom(65565)[0]

        # ip header = first 20 bytes
        ip_header = IP(raw_buffer[0:20])

        print("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))

        # capture ICMP
        if ip_header.protocol == "ICMP":

            # find start of packet
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]

            icmp_header = ICMP(buf)

            print ("ICMP -> Type: %d Code: %d" % (icmp_header.type, icmp_header.code))

            # Check code 3: a host is up but no port available to talk to
            if icmp_header.code == 3 and icmp_header.type == 3:

                # check response lands in subnet
                if IPAddress(ip_header.src_address) in IPNetwork(subnet):

                    if raw_buffer[len(raw_buffer) - len(message):] == message:
                        print
                        "Host Up: %s" % ip_header.src_address

# CTRL+C
except KeyboardInterrupt:

    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
