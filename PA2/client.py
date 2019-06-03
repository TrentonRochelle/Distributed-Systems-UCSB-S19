import math
import datetime
import socket
import sys
import signal
import os
from time import sleep
import threading
import _thread

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def signal_handler(sig, frame):
        print('Exit gracefully!')
        sock.close()
        sys.exit(0)

# def listenThread():
#         while(True):
#                 data_raw = sock.recv(1024)
#                 data_decoded = data.decode('ascii')
#                 print(name + ' received: ' + data_decoded)
    
def main():
        signal.signal(signal.SIGINT, signal_handler)
        sleep(1)
        name = sys.argv[1]
        port = int(sys.argv[2])
        print(name + ' started')
        client = ('localhost',port)
        sock.bind(client)
        server_address = ('localhost', port+10)
        sock.connect(server_address)
        # _thread.start_new_thread(listenThread, ())
        sleep(1)
        while(True):
                response = input("Type 't' to send a transaction or 'p' to print the server's ledger:\n")
                if(response=='t'):
                        person = input("Enter who you'd like to send money to: ")
                        amount = input("How much would you like to send to them? ")
                        if(not is_number(amount)):
                                continue
                        sock.sendall((name + ':' + person + ":" + amount).encode('ascii'))
                        data_raw = sock.recv(1024)
                        data_decoded = data_raw.decode('ascii')
                        print(data_decoded)
                        continue
                elif(response=='p'):
                        sock.sendall(('print').encode('ascii'))
                        # data_raw = sock.recv(1024)
                        # data_decoded = data.decode('ascii')
                        # print(name + ' received: ' + data_decoded)
                        continue
                else:
                        print("Invalid input, try again..")
main()
# kill -2 $(pgrep 'python3')