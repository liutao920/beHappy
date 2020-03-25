import os
import sys
import socket
import select
from dictionary.client import utils


class Dict_client:
    fileno_dict = {}

    def __init__(self):
        self.client_settings = utils.Settings()
        self.epoll = select.epoll()
        self.init_client()

    def init_client(self):
        self.s = socket.socket()
        self.fileno_dict[self.s.fileno()] = self.s
        self.epoll.register(self.s, select.EPOLLOUT|select.EPOLLERR|select.EPOLLIN)
        lr_input = input(self.client_settings.f_lr)
        if lr_input == "q" :
            sys.exit(0)
        else :
            name = input("USER >> ")
            passwd = input("PASSWORD >> ")
            if name or passwd :
                data = lr_input+"@"+ name+"@"+passwd
                self.s.connect(self.client_settings.addr)
                self.s.send(data.encode())

    def client_func(self):
        while True:
            events = self.epoll.poll()
            if events[0][-1] == select.EPOLLIN :
                data = self.s.recv(self.client_settings.buffersize).decode()
                print(self.client_settings.type_code[data])



def main(argl, argv, envp):
    d_c = Dict_client()
    return 0


if "__main__" == __name__:
    sys.exit(main(len(sys.argv), sys.argv, os.environ))