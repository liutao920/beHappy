import os
import hashlib
import logging


class Settings :
    def __init__(self):
        self.mysql_connection_opt = {"host":"localhost", "user":"root", "password":"123456", "port":3306,"charset":"utf8"}
        self.mysql_database_name = "dictionary"
        self.mysql_table_dict = "dict"
        self.mysql_table_user = "user"
        self.mysql_table_history = "history"
        self.__logfile = os.path.join(os.path.dirname(__file__), "server_log.log")
        self.logger = self.__log()
        self.addr = ("localhost", 8888)
        self.buffersize = 1024

    def __log(self):
        logger = logging.getLogger("server_log")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(self.__logfile)
        handler.setLevel(logging.INFO)
        formater = logging.Formatter("[%(filename)s] [%(funcName)s] [%(levelname)s] [%(asctime)s] : %(message)s")
        handler.setFormatter(formater)
        logger.addHandler(handler)
        return logger

    def hash(self, value):
        md5 = hashlib.md5()
        data = md5.update(value)
        return data.hexdigest()