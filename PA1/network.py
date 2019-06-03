#!/usr/bin python3

import socket
import sys
from time import sleep
from datetime import datetime
import threading
import _thread
import signal
from random import randint
sockets = {}


def client_thread(c,port):
    # print('Client thread')
    while True: 
  
        # data received from client 
        data = c.recv(1024)
        # print('Client thread received ' + data.decode('ascii'))
        delay = randint(3,7)
        print('out delay for port ' +str(port) + ' is: ' + str(delay))
        sleep(delay)
        # message = str(datetime.now().time()).encode('ascii')
        message = str(port).encode('ascii')
        server = sockets.get(5005)
        server.sendall(message)
        # c.sendall(message)
        # sockets[0].sendall(data)
        # sockets[1].sendall(data)

  
    # connection closed 
    c.close()

def server_thread(c):
    # print('Server thread')
    while True: 
        # data received from server 
        data = c.recv(1024)
        data = data.decode('ascii')
        # print('Server thread received ' + data)
        port = data[:4]
        time = data[5:].encode('ascii')
        # print('Port: ' + str(port))
        # print('Time: ' + str(time))
        # sleep(randint(3, 7))
        delay2 = randint(3,7)
        print('in delay for port ' +str(port) + ' is: ' + str(delay2))
        sleep(delay2)
        client = sockets.get(int(port))
        client.sendall(time)

        # sleep(1)
        # message = str(datetime.now().time()).encode('ascii')
        # c.sendall(message)
        # sockets[0].sendall(data)
        # sockets[1].sendall(data)

  
    # connection closed 
    c.close()
  
def main():
    # Create a TCP/IP socket
    print('Network started')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    network_address = ('localhost', 10000)
    sock.bind(network_address)
    sock.listen(1)
    while True:
        # Wait for a connection
        while True:
                # print('waiting for a connection')
                connection, client_address = sock.accept()
                sockets.update({client_address[1]:connection})
                if(int(client_address[1])==5001 or int(client_address[1])==5002):
                    print('Port ' + str(client_address[1]) + ' connected')
                    _thread.start_new_thread(client_thread, (connection,client_address[1],)) 
                elif(int(client_address[1])==5005):
                    print('Port ' + str(client_address[1]) + ' connected')
                    _thread.start_new_thread(server_thread, (connection,)) 
                else:
                    print("error!!!")



main()