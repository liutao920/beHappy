import os
import sys
import time
import socket
import select
from dictionary.server import utils
from dictionary.server import mysql_work


class Dict_server :

    fileno_dict = {}
    addr_dict = {}
    name_dict = {}

    def __init__(self):
        self.mysql_fun = mysql_work.Mysql_opt()
        self.epoll = select.epoll()
        self.init_server()
        self.server_func()

    def init_server(self):
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.fileno_dict[self.s.fileno()] = self.s
        self.epoll.register(self.s,select.EPOLLIN|select.EPOLLET)
        self.s.bind(self.mysql_fun.settings.addr)
        self.s.listen(5)

    def server_func(self):
        while True :
            # print("waitting to connect...")
            events = self.epoll.poll()
            for event in events :
                if self.fileno_dict[event[0]]==self.s :
                    c, addr = self.s.accept()
                    self.mysql_fun.settings.logger.info("connect from %s"%repr(addr))
                    self.fileno_dict[c.fileno()] = c
                    self.addr_dict[event[0]] = c.getpeername()
                    self.epoll.register(c, select.EPOLLIN|select.EPOLLERR|select.EPOLLET|select.EPOLLHUP)

                else :

                    if event[-1]&select.EPOLLIN :
                        data = self.fileno_dict[event[0]].recv(self.mysql_fun.settings.buffersize).decode()
                        if "@" in data :
                            data_lst = data.split("@")
                            if data_lst[0] == "1" :
                                self.__login(event, data_lst[1:])
                            elif data_lst[0] == "2" :
                                self.__regist(event, data_lst[1:])
                            elif data_lst[0] == "3":
                                self.__look_up(event, data_lst[1])
                            elif data_lst[0] == "4":
                                self.__check_history(event)
                            else :
                                self.mysql_fun.settings.logger.info("IMPOSSIBLE %s" % data)

                        elif not data :
                            print(self.addr_dict)
                            self.mysql_fun.settings.logger.info("%s断开连接" % repr(self.addr_dict.get(event[0])))
                            if event[0] in self.name_dict :
                                self.name_dict.pop(event[0])
                            self.epoll.unregister(event[0])
                            self.fileno_dict.pop(event[0])


    def __login(self, event, data_lst):
        name = data_lst[0]
        if name in self.name_dict.values():
            c_num = list(self.name_dict.keys())[list(self.name_dict.values()).index(name)]
            print(c_num,event[0])
            self.fileno_dict[c_num].send(b"1@502")
        passwd = self.mysql_fun.settings.hash(data_lst[-1])
        sql = "select passwd from %s where name=%r;" % (self.mysql_fun.settings.mysql_table_user, name)
        password = self.mysql_fun.select_info(sql)
        if not password :
            self.fileno_dict[event[0]].send(b"1@402")
        else :
            password = password[0][0]
            if password != passwd :
                self.fileno_dict[event[0]].send(b"1@402")
            else :
                self.name_dict[event[0]] = name
                self.fileno_dict[event[0]].send(b"1@201")

    def __regist(self, event, data_lst):
        name = data_lst[0]
        sql = "select name from %s where name=%r;" % (self.mysql_fun.settings.mysql_table_user, name)
        isexist = self.mysql_fun.select_info(sql)
        if not isexist:
            passwd = self.mysql_fun.settings.hash(data_lst[-1])
            sql = "insert into %s(name,passwd) values (%r,%r);" % (self.mysql_fun.settings.mysql_table_user, name, passwd)
            res = self.mysql_fun.insert_info(sql)
            if res:
                self.name_dict[event[0]] = name
                self.fileno_dict[event[0]].send(b"2@200") #返回类型200,注册成功
            else:
                self.fileno_dict[event[0]].send(b"2@501") #返回错误类型501,服务器异常
        else :
            self.fileno_dict[event[0]].send(b"2@401") #返回错误类型401,重名

    def __look_up(self, event, word):
        sql = "select meanings from %s where word=%r" % (self.mysql_fun.settings.mysql_table_dict, word)
        word_mean = self.mysql_fun.select_info(sql)
        if not word_mean :
            self.fileno_dict[event[0]].send(b"3@403")
        else :
            res = "3@%s" % word_mean[0][0]
            self.fileno_dict[event[0]].send(res.encode())
            self.__save_history(event, word, word_mean[0][0])

    def __save_history(self, event, word, means):
        sql = "insert into %s(name, word, meanings) values (%r,%r,%r)" % (self.mysql_fun.settings.mysql_table_history, self.name_dict[event[0]], word, means)
        res = self.mysql_fun.insert_info(sql)
        if not res :
            self.mysql_fun.settings.logger.warning("history insert error")

    def __check_history(self, event):
        sql = "select word,meanings,his_date from %s where name=%r limit 10"% (self.mysql_fun.settings.mysql_table_history, self.name_dict[event[0]])
        his = self.mysql_fun.select_info(sql)
        res = "4@%s"%repr(his)
        self.fileno_dict[event[0]].send(res.encode())




def main(argl, argv, envp):
    d_s = Dict_server()
    return 0

if "__main__" == __name__ :
    sys.exit(main(len(sys.argv), sys.argv, os.environ))