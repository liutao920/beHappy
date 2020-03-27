import os
import logging


class Settings :
    def __init__(self):
        self.mysql_table_dict = "dict"
        self.mysql_table_user = "user"
        self.mysql_table_history = "history"
        self.__logfile = os.path.join(os.path.dirname(__file__), "client_log.log")
        self.logger = self.__log()
        self.addr = ("localhost", 8888)
        self.buffersize = 1024
        self.selection = ["1", "2"]
        self.f_lr = """
                    ===========================
                              MENU
                        1.LOG IN(press 1);
                        
                        2.REGIST(press 2);
                        
                        q.QUIT(press q);
                    ===========================
                        >> """
        self.f_ss = """
                    ===========================
                              MENU
                        3.LOOK UP(press 3);

                        4.CHECK HISTORY(press 4);

                        q.QUIT(press q);
                    ===========================
                        >> """
        self.type_code = {
            "200":"注册成功",
            "201":"登录成功",
            "401":"注册失败,重名警告",
            "402":"登录失败,用户名或密码错误",
            "403":"X, no such word",
            "501":"注册失败,服务器异常",
            "502":"其他客户端登录,强制退出"
        }

    def __log(self):
        logger = logging.getLogger("client_log")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(self.__logfile)
        handler.setLevel(logging.INFO)
        formater = logging.Formatter("[%(filename)s] [%(funcName)s] [%(levelname)s] [%(asctime)s] : %(message)s")
        handler.setFormatter(formater)
        logger.addHandler(handler)
        return logger