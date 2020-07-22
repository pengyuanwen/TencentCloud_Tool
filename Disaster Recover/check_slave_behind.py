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

    def check_subordinate_status(self):
        sql = "show subordinate status;"
        ret = self.conn_query(sql)
        self.close()
        return ret


ip = open(r'/home/yuanwen.peng/scripts/python/qiehuan/check_slave_behind.cfg', 'r')
content = ip.readlines()
for i in content:
    # result = i.strip('\n')
    mysql = Check_Mysql(i)
    ret = mysql.check_subordinate_status()
    slag = ret[0][32]
    print "ip:%s,延迟时间:%s" % (i.strip('\n'), slag)