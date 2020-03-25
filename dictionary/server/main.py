import os
import sys
import socket
import select
from dictionary.server import utils
from dictionary.server import mysql_work


class Dict_server :
    fileno_dict = {}
    def __init__(self):
        self.server_settings = utils.Settings()
        self.mysql_fun = mysql_work.Mysql_opt()
        self.epoll = select.epoll()
        self.init_server()

    def init_server(self):
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.fileno_dict[self.s.fileno()] = self.s
        self.epoll.register(self.s,select.EPOLLIN)
        self.s.bind(self.server_settings.addr)
        self.s.listen(5)

    def server_func(self):
        while True :
            print("waitting to connect...")
            events = self.epoll.poll()
            for event in events :
                if self.fileno_dict[event[0]]==self.s :
                    c, addr = self.s.accept()
                    self.server_settings.logger.info("connect from %s"%repr(addr))
                    self.fileno_dict[c.fileno()] = c
                    self.epoll.register(c, select.EPOLLIN|select.EPOLLOUT|select.EPOLLERR)

                else :
                    if event[-1]==select.EPOLLIN :
                        data = self.fileno_dict[event[0]].recv(self.server_settings.buffersize).encode()
                        if "@" in data :
                            data_lst = data.split("@")
                            if data_lst[0] == 1 :
                                self.__login(event, data_lst[1:])
                            elif data_lst[0] == 2 :
                                self.__regist(event, data_lst[1:])

    def __login(self, event, data_lst):
        pass

    def __regist(self, event, data_lst):
        name = data_lst[0]
        sql = "select name from %s where name=%s;" % (self.server_settings.mysql_table_user, name)
        isexist = self.mysql_fun.select_info(sql)
        if not isexist:
            passwd = self.server_settings.hash(data_lst[-1])
            sql = "insert into %s(name,passwd) values (%r,%r);" % (self.server_settings.mysql_table_user, name, passwd)
            res = self.mysql_fun.insert_info(sql)
            if res:
                self.fileno_dict[event[0]].send(b"200") #返回类型200,注册成功
            else:
                self.fileno_dict[event[0]].send(b"501") #返回错误类型501,服务器异常
        else :
            self.fileno_dict[event[0]].send(b"401") #返回错误类型401,重名






def main(argl, argv, envp):
    d_s = Dict_server()
    return 0

if "__main__" == __name__ :
    sys.exit(main(len(sys.argv), sys.argv, os.environ))