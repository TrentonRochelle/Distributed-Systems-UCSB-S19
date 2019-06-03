import math
from datetime import datetime, timedelta
import socket
import signal
import sys
import os
from time import sleep
import configparser
import threading
import _thread
import queue
from queue import PriorityQueue
from collections import defaultdict,deque
sockets = {}
clientAddresses = []
clientToAddress = {}
requestQ = PriorityQueue()
ledger = []
indexMap = defaultdict(list)
index = 0
networkPort = 0
networkPortNative = 0
ServerPorts = []
myPort = 0
names = []
lamportTime = 0
serverId = 0
currentReplies = 0
maxReplies = 2
accessTime = 0
textString = ""

def readLedgerTxt(string):
        global index
        with open(string, "r") as ins:
                for line in ins:
                        line = line[:-1]
                        array = line.split(':')
                        ledger.append(array)
                        if(len(array)==2):
                                if array[0] not in indexMap.keys():
                                        indexMap[array[0]] = []
                                indexMap[array[0]].append(index)
                        else:
                                if array[0] not in indexMap.keys():
                                        indexMap[array[0]] = []
                                indexMap[array[0]].append(index)
                                if array[1] not in indexMap.keys():
                                        indexMap[array[1]] = []
                                indexMap[array[1]].append(index)  
                        index = index + 1                

def printLedgerInfo():
        print(ledger)
        print(indexMap)
        for key in indexMap.keys():
                amount = getAccountBalance(key)
                print(key + ' has ' + str(amount) + ' dollars')

def getAccountBalance(name):
        if name not in indexMap.keys():
                return -1
        balance = 0
        first = True
        for i in indexMap[name]: #returns indices in ledger
                if first:
                        first = False
                        balance = int(ledger[i][1])
                else:
                        transaction = ledger[i]
                        if(transaction[0]==name):
                                balance-= int(transaction[2])
                                if(transaction[1]==name):
                                        balance+= int(transaction[2])
                        else:
                                balance+= int(transaction[2])
        return balance

def signal_handler(sig, frame):
        print('Exit gracefully!')
        for i in clientAddresses:
                c = sockets.get(i)
                c.close()
        sys.exit(0)

def listenClientThread(c, port):
        while(True):
                data = c.recv(1024)
                _thread.start_new_thread(processClientData, (c,port,data,))

def processClientData(c,port, data):
        global lamportTime
        data_decoded = data.decode('ascii')
        if(data_decoded != ""):
                array = data_decoded.split(':')
                        #data from client
                if(array[0]=='print'):
                        printLedgerInfo()
                else:
                        if(array[1] not in names or array[1] not in names):
                                c.sendall("Unknown name to send to".encode('ascii'))
                        else:
                                lamportTime+=1
                                print("Transaction received from " + array[0] + lamportToString())
                                # qTrans.put(data_decoded)
                                processRequest(data_decoded)


        else:
                print('Server receiving nothing...client is probably closed...closing now')
                c.close()
                sleep(1)
        return

def processRequest(data_decoded):
        global networkPortNative
        global myPort
        global lamportTime
        lamportTime+=1
        # print("data decoded: " + data_decoded)
        requestQ.put(((lamportTime,serverId),[lamportTime,serverId,data_decoded]))
        for port in ServerPorts:
                p = str(port)
                message = 'REQUEST'
                message = p + ":" + str(networkPort) + ":" + str(lamportTime) + ":" + str(serverId) + ':' + message + ":" + str(lamportTime) + ":"
                network = sockets.get(networkPortNative)
                # print('sending to port ' + p +':'+message)
                network.sendall(message.encode('ascii'))
                sleep(.01)
        print("REQUEST <" + str(lamportTime) + ',' + str(serverId) + "> sent to all.")

def listenNetworkThread(socket):
        while(True):
                data = socket.recv(1024)
                _thread.start_new_thread(processNetworkData, (data,))

def processNetworkData(data):
        global lamportTime
        global currentReplies
        global index
        global requestQ
        data_decoded = data.decode('ascii')
        if(data_decoded != ""):
                data_array = data_decoded.split(':')
                port = data_array[0]
                requestLamport = data_array[1]
                requestId= data_array[2]
                receivedLamport = data_array[4]
                message = data_array[3]
                lamportTime = max(int(receivedLamport),lamportTime) + 1
                # print("")
                # print("Received from port " + port + ':' + message + lamportToString(lamportTime))
                lampId = lamportToString()
                print(message + pairToString(requestLamport,requestId) + "received from server " + str(int(port)%10) + lampId)
                if(message=="REQUEST"):
                        lamportTime+=1
                        lampId = lamportToString()
                        requestQ.put(((int(requestLamport),int(requestId)),[lamportTime,port,""]))
                        message = "REPLY"
                        message = port + ":" + str(networkPort) + ":" + str(requestLamport) + ":" + requestId + ':' + message + ":" + str(lamportTime) + ":"
                        network = sockets.get(networkPortNative)
                        # lampId = lamportToString()
                        print("REPLY"+ pairToString(requestLamport,requestId) + "sent to server " + str(int(port)%10) + lampId)
                        network.sendall(message.encode('ascii'))
                        return
                elif(message=="REPLY"):
                        # print("")
                        currentReplies+=1
                        # if(currentReplies==maxReplies): #can now access resource if own request is at the head of the queue
                        #         currentReplies-=maxReplies
                        #         front = requestQ.get()
                        #         if(front[1][2]!=""): #own resource is at head of deque -> access the critical section
                        #                 # front = requestQ.pop()[1]
                        #                 # trans = front.split(":") #From, To, Amount
                        #                 trans = front[1][2].split(":")
                        #                 lamportTime+=1
                        #                 print("Run Critical Section for" + pairToString(requestLamport,requestId) + lamportToString())
                        #                 currentTime = datetime.now()
                        #                 releaseTime = (currentTime + timedelta(seconds=accessTime)).time()
                        #                 print("Ledger opened: "+ str(currentTime.time()))
                        #                 ledgerTxt = open(textString, "a+")
                        #                 total = getAccountBalance(trans[0])
                        #                 message = ""
                        #                 releaseString = ""
                        #                 if(total>=int(trans[2])): # valid transaction
                        #                         print("Request is valid")
                        #                         ledger.append(trans)
                        #                         indexMap[trans[0]].append(index)
                        #                         indexMap[trans[1]].append(index)
                        #                         index+=1
                        #                         ledgerTxt.write((front[1][2]+"\n"))
                        #                         message = "Successfully sent " + trans[1] + " " + trans[2] + " dollars"
                        #                         releaseString = front[1][2]
                        #                 else: #invalid transaction, send back to client
                        #                         print("Request is invalid")
                        #                         message = "Insufficient funds for this transaction. You have " + str(total) + " dollars."
                        #                         releaseString = ""
                        #                 time = datetime.now().time()
                        #                 while(time < releaseTime):
                        #                         time = datetime.now().time()
                        #                 ledgerTxt.close()
                        #                 print("Ledger closed: " + str(datetime.now().time()))

                        #                 #send release now
                        #                 lamportTime+=1
                        #                 for port in ServerPorts:
                        #                         p = str(port)
                        #                         m = 'RELEASE'
                        #                         m = p + ":" + str(networkPort) + ":" + str(requestLamport) + ":" + str(requestId) + ':' + m + ":" + str(lamportTime) + ":" + releaseString + ""
                        #                         network = sockets.get(networkPortNative)
                        #                         # print('sending to port ' + p +':'+m)
                        #                         network.sendall(m.encode('ascii'))
                        #                         sleep(.01)
                        #                 print("RELEASE <" + str(requestLamport) + ',' + str(requestId) + "> sent to all." + lamportToString())
                        #                 name = trans[0]
                        #                 c = sockets.get(clientToAddress[name])
                        #                 c.sendall(message.encode('ascii'))
                        #                 return
                        #         else: #wait until own request is at head of queue
                        #                 requestQ.put(front)
                        #                 return
                        access(requestLamport,requestId)
                        return
                elif(message=="RELEASE"):
                        To = data_array[5]
                        if(To == ""):
                                front = requestQ.get()
                                return
                        From = data_array[6]
                        Amount = data_array[7]
                        trans = To + ":" + From + ":" + Amount
                        ledger.append([To,From,Amount])
                        indexMap[To].append(index)
                        indexMap[From].append(index)
                        index+=1
                        ledgerTxt = open(textString, "a+")
                        ledgerTxt.write((trans+"\n"))
                        ledgerTxt.close()
                        front = requestQ.get()
                        # print(front)
                        # print("Releasing the following:")
                        # print(front)
                        access(requestLamport,requestId)


                        


                        return
                else:
                        print("Message is not request, reply, or release. What are you doing?")
                        return


def access(requestLamport,requestId):
        global lamportTime
        global currentReplies
        global index
        global requestQ
        # print(requestQ)
        # print("Current Replies: " + str(currentReplies))
        if(currentReplies==maxReplies): #can now access resource if own request is at the head of the queue
                front = requestQ.get()
                # print("Here's the front:")
                # print(front)
                if(front[1][2]!=""): #own resource is at head of deque -> access the critical section
                        currentReplies-=maxReplies
                        # front = requestQ.pop()[1]
                        # trans = front.split(":") #From, To, Amount
                        trans = front[1][2].split(":")
                        lamportTime+=1
                        print("Run Critical Section for" + pairToString(requestLamport,requestId) + lamportToString())
                        currentTime = datetime.now()
                        releaseTime = (currentTime + timedelta(seconds=accessTime)).time()
                        print("Ledger opened: "+ str(currentTime.time()))
                        ledgerTxt = open(textString, "a+")
                        total = getAccountBalance(trans[0])
                        message = ""
                        releaseString = ""
                        if(total>=int(trans[2])): # valid transaction
                                print("Request is valid")
                                ledger.append(trans)
                                indexMap[trans[0]].append(index)
                                indexMap[trans[1]].append(index)
                                index+=1
                                ledgerTxt.write((front[1][2]+"\n"))
                                message = "Successfully sent " + trans[1] + " " + trans[2] + " dollars"
                                releaseString = front[1][2]
                        else: #invalid transaction, send back to client
                                print("Request is invalid")
                                message = "Insufficient funds for this transaction. You have " + str(total) + " dollars."
                                releaseString = ""
                        time = datetime.now().time()
                        while(time < releaseTime):
                                time = datetime.now().time()
                        ledgerTxt.close()
                        print("Ledger closed: " + str(datetime.now().time()))

                        #send release now
                        lamportTime+=1
                        for port in ServerPorts:
                                p = str(port)
                                m = 'RELEASE'
                                m = p + ":" + str(networkPort) + ":" + str(requestLamport) + ":" + str(requestId) + ':' + m + ":" + str(lamportTime) + ":" + releaseString + ""
                                network = sockets.get(networkPortNative)
                                # print('sending to port ' + p +':'+m)
                                network.sendall(m.encode('ascii'))
                                sleep(.01)
                        print("RELEASE <" + str(requestLamport) + ',' + str(requestId) + "> sent to all." + lamportToString())
                        name = trans[0]
                        c = sockets.get(clientToAddress[name])
                        c.sendall(message.encode('ascii'))
                        return
                else: #wait until own request is at head of queue
                        requestQ.put(front)
                        return

def pairToString(lamport,id):
        return (" <" + str(lamport) + "," + str(id) + "> ")
                        

def lamportToString():
        return " (Logical time: " + str(lamportTime) + ")"

def main():
        global networkPortNative
        global networkPort
        global serverId
        global accessTime
        global textString
        print(sys.argv[1] + " started (Logical time: " + str(lamportTime)+ ")")
        accessTime = int(sys.argv[2])
        signal.signal(signal.SIGINT, signal_handler)
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read('config.ini')
        ClientPort = int(config[sys.argv[1]]['ClientPort'])
        NetworkPort = int(config[sys.argv[1]]['NetworkPort'])
        networkPort = NetworkPort
        networkPortNative = int(config['Network']['Port'])
        for key in config['Servers'].keys():
                server = key
                if server != sys.argv[1]: 
                        serverNetworkPort = config[server]['NetworkPort']
                        ServerPorts.append(serverNetworkPort)
        for name in config['Clients'].keys():
                names.append(name)
                clientToAddress[name]=int(config['Clients'][name])
        # _thread.start_new_thread(queueThread, ()) 
        num = config['Servers'][sys.argv[1]] 
        textString = 'ledger' +num + '.txt'
        serverId = int(num)
        readLedgerTxt(textString)
        # printLedgerInfo()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server = ('localhost',ClientPort)
        sock.bind(server)
        # sock.listen(1)
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        network = ('localhost', NetworkPort)
        sock2.bind(network)
        network_address = ('localhost', networkPortNative)
        sock2.connect(network_address)
        sockets.update({networkPortNative:sock2})
        _thread.start_new_thread(listenNetworkThread, (sock2,))
        # _thread.start_new_thread(queueThread, ())

        sock.listen(1)
        while(True):
                connection, client_address = sock.accept()
                sockets.update({client_address[1]:connection})
                clientAddresses.append(client_address[1])
                print('Port ' + str(client_address[1]) + ' connected')
                _thread.start_new_thread(listenClientThread, (connection,client_address[1],)) 


main()