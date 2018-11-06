#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author:yuanwen.peng
#time:2018-06-12
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import pymysql

class DB_API(object):

    def __init__(self,host):
        self.host = host
        self.re_all = []

    def get_conn(self):
        try:
            self.conn = pymysql.connect(
                host = self.host,
                port = 3306,
                user = 'user',
                passwd = 'passwd',
                db = '',
                charset = 'utf8'
            )
        except pymysql.Error,e:
            errormag = 'Connot connect to server\nERROR (%s): %s' %(e.args[0],e.args[1])
            print errormag
            sys,exit()

    def query(self,select_sql):
        cursor = self.conn.cursor()
        cursor.execute(select_sql)
        result = cursor.fetchall()
        self.conn.commit()
        return result
        cursor.close()

    def __del__(self):
        self.conn.close()
