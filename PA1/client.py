import math
import datetime
import socket
import sys
import os
from time import sleep

class clientt:
    def __init__(self):
        self.t1 = -1
        self.t2 = -1
        self.sim_time_sync = -1
        self.sys_time_sync = -1
        self.sim_time_current = -1
        self.rho = 0.5
        self.delta = 10
        self.syncTime = self.delta/(2*self.rho)

    def set_t1(self):
        self.set_sim_time_current()
        self.t1 = self.sim_time_current
    def set_t2(self):
        self.set_sim_time_current()
        self.t2 = self.sim_time_current
    def set_sim_time_sync(self,val):
        self.sim_time_sync = val+(self.t2-self.t1)/2
    def set_sys_time_sync(self):
        self.sys_time_sync = datetime.datetime.now()
    def set_sim_time_current(self):
        self.sim_time_current = self.sim_time_sync + (datetime.datetime.now()-self.sys_time_sync)*(1+self.rho)
    
def main():
    sleep(2)
    print('Client started')
    num = str(sys.argv[1])
    # print('client')
    cli = clientt()
    cli.sim_time_sync = datetime.datetime.now()
    cli.sys_time_sync = datetime.datetime.now()
    cli.sim_time_current = datetime.datetime.now()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = ('localhost',int(sys.argv[1])+5000)
    sock.bind(client)
    network_address = ('localhost', 10000)
    sock.connect(network_address)

    while(True):
        print('Client ' + num +' true time: ' + str(datetime.datetime.now()))
        cli.set_sim_time_current()
        print('Client ' + num + ' sim time: ' + str(cli.sim_time_current))
        print('Sending time request from client '+num)
        cli.set_t1()
        sock.sendall(('time request from client '+num).encode('ascii'))      
        data = sock.recv(1024)
        time = data.decode('ascii')
        dt = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
        cli.set_t2()
        cli.set_sim_time_sync(dt)
        cli.set_sys_time_sync()
        print('Client '+ num + ' received time: ' + time)
        print('Client ' + num +' true time: ' + str(datetime.datetime.now()))
        cli.set_sim_time_current()
        print('Client ' + num + ' sim time: ' + str(cli.sim_time_current))
        # cli.set_sys_time_sync(data.decode('ascii'))
        sleep(cli.syncTime)

main()
# kill $(pgrep 'python3')