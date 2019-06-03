import math
from datetime import datetime
import socket
import sys
import os
from time import sleep

def main():
    sleep(1)
    print("Server started")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server = ('localhost',5005)
    sock.bind(server)
    network_address = ('localhost', 10000)
    sock.connect(network_address)  
    while(True):
        data = sock.recv(1024)
        print('Server received: '+ data.decode('ascii'))
        time = str(datetime.now())
        print('Server sending time: ' + time)
        sock.sendall((data.decode('ascii')+':'+time).encode('ascii')) 

main()