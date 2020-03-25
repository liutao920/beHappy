import pymysql
import warnings
import re
from dictionary.server import utils

class Mysql_opt :
    #数据库的链接
    warnings.filterwarnings("ignore")
    def __init__(self):
        self.mysql_settings = utils.Settings()
        self.__conn = pymysql.connect(**self.mysql_settings.mysql_connection_opt)
        self.__cur = self.__conn.cursor()
        self.__init_database()
        self.__init_word_book()
        self.__dict_book()
        self.__init_user()
        self.__init_history()


    def __init_database(self):
        build_database = "create database if not exists %s;" %self.mysql_settings.mysql_database_name
        select_database = "use %s" %self.mysql_settings.mysql_database_name
        self.__cur.execute(build_database)
        self.__cur.execute(select_database)

    def __init_word_book(self):
        build_table_dictinfo = "create table if not exists %s ( id int auto_increment primary key, \
                                                                        word varchar(30) unique,\
                                                                        meanings varchar(256) );" % self.mysql_settings.mysql_table_dict
        self.__cur.execute(build_table_dictinfo)

    def __dict_book(self):
        self.__cur.execute("select word from %s limit 3"%self.mysql_settings.mysql_table_dict)
        tables = self.__cur.fetchall()
        if tables :
            return
        self.mysql_settings.logger.warning("init database and dict table...")
        pattern = re.compile("[\s]+")
        with open(r"./dict.txt") as f:
            for line in f:
                line_lst = pattern.split(line)
                w = line_lst[0]
                m = " ".join([x.strip() for x in line_lst[1:] if x])
                sql = "insert into %s(word,meanings) values (%r,%r);" % (self.mysql_settings.mysql_table_dict, w, m)
                try :
                    self.__cur.execute(sql)
                except Exception as e:
                    self.mysql_settings.logger.warning("%s is %s" % (line, e))
            self.__conn.commit()
        self.mysql_settings.logger.warning("init done...")

    def __init_user(self):
        build_table_user = "create table if not exists %s (id int auto_increment primary key, \
                                                            name varchar(30) unique, \
                                                            passwd varchar(128));" % self.mysql_settings.mysql_table_user
        self.__cur.execute(build_table_user)

    def __init_history(self):
        build_table_history = "create table if not exists %s (id int auto_increment primary key, \
                                                                    name varchar(30), \
                                                                    word varchar(30), \
                                                                    his_date timestamp);" % self.mysql_settings.mysql_table_history
        self.__cur.execute(build_table_history)

    def insert_info(self, sql):
        try :
            self.__cur.execute(sql)
            self.__conn.commit()
        except Exception as e:
            self.mysql_settings.logger.warning("%s插入失败" % sql)
            return 0
        return 1

    def select_info(self, sql):
        try :
            self.__cur.execute(sql)
        except Exception as e:
            self.mysql_settings.logger.warning("%s查询失败" % sql)
            return 0
        return self.__cur.fetchall()
