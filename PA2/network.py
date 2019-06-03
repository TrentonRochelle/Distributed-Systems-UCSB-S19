#!/usr/bin python3

import socket
import sys
from time import sleep
from datetime import datetime, timedelta
import threading
import _thread
import signal
import queue
# import configparser
import random
sockets = {}
clientAddresses = []
qNetwork = queue.Queue()
# portToQueueIndex = {}
# queues = []
# index = 0
# config = ConfigParser.ConfigParser()
#         config.read('config.ini')
#         for key in config['Servers'].keys():
#                 portsToQueueIndex.update({key:index})
#                 queues.append(queue.Queue())
#                 index = index + 1

def listenThread(c,port):
        # print('Client thread')
        while True: 
                data = c.recv(1024)
                # sendThread(port)
                # _thread.start_new_thread(sendThread, (port,data,))
                _thread.start_new_thread(processReceivedData, (data,))

                # print('Client thread received ' + data.decode('ascii'))
                # delay = randint(1,3)
                # print('out delay for port ' +str(port) + ' is: ' + str(delay))
                # sleep(delay)
                # message = str(datetime.now().time()).encode('ascii')
                # message = str(port).encode('ascii')
                # server = sockets.get(5005)
                # server.sendall(message)
                # c.sendall(message)
                # sockets[0].sendall(data)
                # sockets[1].sendall(data)

        
        # connection closed 
        c.close()

def processReceivedData(data):
        data = data.decode('ascii')
        if(data!=""):
                # print("data received to put in queue is: " + data)
                delay = random.uniform(1,4)
                sendTime = (datetime.now() + timedelta(milliseconds=delay*1000)).time()
                # messageArray = data.split(':')
                # port = int(array[0])
                # messageArray.pop(0)
                # s = ''
                # s.join(messageArray)
                array = [sendTime,data,delay]
                qNetwork.put(array)


# def sendThread(port,data):
#         # index = portToQueueIndex.get(str(port))
#         data = data.decode('ascii')
#         if(data!=""):
#                 print("data is: " + data)
#         # delay = random.uniform(.1, 1)
#         # array = data.split(':')
#         # port = int(array[0])
#         # message = array[1]
#         # server = sockets.get(port)
#         # sleep(delay)
#         # server.sendall(message.encode('ascii'))
#         # sendTime = datetime.now().time() + datetime.timedelta(milliseconds=delay*1000)
#         # timeAndData = [sendTime,data]
#         # queues[index].put(timeAndData)


    
def queueThread():
        while(True):
                if(not qNetwork.empty()):
                        head = qNetwork.get()
                        time = datetime.now().time()
                        while(time < head[0]):
                                time = datetime.now().time()
                        array = head[1].split(':')
                        delay = head[2]
                        toPort = int(array[0])
                        array.pop(0)
                        # print(array)
                        message = ':'
                        message = message.join(array)
                        server = sockets.get(toPort)
                        array = message.split(':')
                        # print("Sending to port "+ str(toPort)+ " the following:" + message)
                        print(array[3] + " <" + array[1] + "," + array[2] + "> from server " + str(int(array[0])%10) + "->" + str(toPort%10) + " (delay " + str(round(delay,2)) + " seconds)")
                        server.sendall(message.encode('ascii'))
                else:
                        continue


def signal_handler(sig, frame):
        print('Exit gracefully!')
        for i in clientAddresses:
                c = sockets.get(i)
                c.close()
        sys.exit(0)

def main():
        # Create a TCP/IP socket
        print('Network started')
        _thread.start_new_thread(queueThread, ())
        signal.signal(signal.SIGINT, signal_handler)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        network_address = ('localhost', 10000)
        sock.bind(network_address)
        sock.listen(1)
        while True:
                # Wait for a connection
                while True:
                        # print('waiting for a connection')
                        connection, client_address = sock.accept()
                        sockets.update({client_address[1]:connection})
                        clientAddresses.append(client_address[1])
                        print('Port ' + str(client_address[1]) + ' connected')
                        _thread.start_new_thread(listenThread, (connection,client_address[1],)) 




main()