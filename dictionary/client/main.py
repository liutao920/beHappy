import os
import sys
import re
import time
import socket
import select
import datetime
from dictionary.client import utils


class Dict_client:

    word = None

    def __init__(self):
        self.client_settings = utils.Settings()
        self.__epoll = select.epoll()
        self.__init_client()
        self.__client_func()

    def __init_client(self):
        self.s = socket.socket()
        self.__epoll.register(self.s, select.EPOLLERR|select.EPOLLIN|select.EPOLLET)
        self.__func_check()

    def __func_check(self):
        lr_input = input(self.client_settings.f_lr)
        if lr_input == "q":
            sys.exit(0)
        elif lr_input in self.client_settings.selection:
            name = input("USER >> ")
            passwd = input("PASSWORD >> ")
            if name and passwd:
                data = lr_input + "@" + name + "@" + passwd
                self.s.connect(self.client_settings.addr)
                self.s.send(data.encode())
        else :
            print("错误选项,1s 后跳转至功能选项界面...")
            time.sleep(1)
            self.__func_check()

    def __client_func(self):
        while True:
            print("waitting for IO...")
            events = self.__epoll.poll()
            if events[0][-1] == select.EPOLLIN :
                data = self.s.recv(self.client_settings.buffersize).decode()
                data_lst = data.split("@")
                if data_lst[0] == "1" or data_lst[0] == "2":
                    print(self.client_settings.type_code.get(data_lst[1], "未定义代码"))
                    if not data_lst[1].startswith("2"):
                        self.__jump_login()
                        self.client_settings.logger.info(self.client_settings.type_code.get(data_lst[1], "未定义代码"))
                    else :
                        self.word = self.__success_login()
                elif data_lst[0] == "3" :
                    word_mean = self.client_settings.type_code.get(data_lst[1], data_lst[1])
                    print("%s ==> %s" % (self.word, word_mean))
                    self.word = self.__look_up()
                elif data_lst[0] == "4":
                    print("HISTORY >> ")
                    # print(data_lst[1])
                    self.__print_history(data_lst[1])
                    input("press anything to continue...")
                    self.__success_login()
                else :
                    print("IMPOSSIBLE")

    def __jump_login(self):
            self.s.close()
            while True:
                print("1s 后跳转至功能选项界面...")
                time.sleep(1)
                break
            self.__func_check()

    def __success_login(self):
        ss_input = input(self.client_settings.f_ss)
        if ss_input == "q" :
            self.__jump_login()
        elif ss_input == "3" :
            return self.__look_up()
        elif ss_input == "4" :
            self.__check_history()
        else:
            print("WRONG SELECTION")
            self.__success_login()

    def __look_up(self):
        w_input =  input("WORD PLEASE >> ")
        if w_input == "q" :
            self.__success_login()
        else :
            word_check = "3@%s"%w_input
            self.s.send(word_check.encode())
            return w_input

    def __check_history(self):
        his_check = "4@"
        self.s.send(his_check.encode())

    def __print_history(self, data):
        data = data[1:-1]
        if not data :
            print("没有查询历史记录...")
        else :
            #匹配以获取每条历史记录
            pattern1 = re.compile(r"\(([\s\S]+?\)),")
            #匹配单条历史记录以获取单词和单词意思
            pattern2 = re.compile(r"\', ")
            print("%-30s"%"WORD", "%-100s"%"MEANS", "DATE")
            his_list = pattern1.findall(data)
            for his in his_list :
                per_his = pattern2.split(his)
                word_his = per_his[0][1:]
                mean_his = per_his[1][1:]
                if len(mean_his)>100:
                    mean_his = mean_his[:97]+"..."
                date_his = tuple(per_his[-1][18:-2].split(","))
                print("%-30s"%word_his, "%-100s"%mean_his, "%s-%s-%s %s:%s:%s"%date_his)

def main(argl, argv, envp):
    d_c = Dict_client()
    return 0


if "__main__" == __name__:
    sys.exit(main(len(sys.argv), sys.argv, os.environ))