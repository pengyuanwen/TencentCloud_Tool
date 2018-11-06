# -*- encoding:utf-8 -*-
#author：yuanwen.peng
#time : 2018-06-04
import MySQLdb
import os
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class Check_Mysql():
    def __init__(self, host, charset="utf8"):
        self.conn = MySQLdb.connect(host=host, port=3306, user='user', passwd='', db='',
                                    charset="utf8")
        # self.conn.select_db(database)
        self.cur = self.conn.cursor()

    def conn_query(self, sql):
        rel = self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    def close(self):
        self.cur.close()
        self.conn.close()

    def check_readonly(self):
        sql = "show variables like \'read_only\';"
        ret = self.conn_query(sql)
        self.close()
        return ret


ip = open(r'/home/yuanwen.peng/scripts/python/qiehuan/check_readonly.cfg', 'r')
content = ip.readlines()
for i in content:
    mysql = Check_Mysql(i)
    ret = mysql.check_readonly()
    info = list(ret)
    read_only = info[0][0]
    read_only_status = info[0][1]
    print "ip:%s,read_only=%s" % (i.strip('\n'), read_only_status)