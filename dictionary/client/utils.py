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
        self.f_lr = """
                    ===========================
                              MENU
                        1.LOG IN(press 1);
                        
                        2.REGIST(press 2);
                        
                        3.QUIT(press q);
                    ===========================
                        >> """
        self.type_code = {
            "200":"OK",
            "401":"注册失败,重名警告",
            "501":"注册失败,服务器异常"
        }

    def __log(self):
        logger = logging.getLogger("client_log")
        logger.setLevel(logging.WARNING)
        handler = logging.FileHandler(self.__logfile)
        handler.setLevel(logging.WARNING)
        formater = logging.Formatter("[%(filename)s] [%(funcName)s] [%(levelname)s] [%(asctime)s] : %(message)s")
        handler.setFormatter(formater)
        logger.addHandler(handler)
        return logger