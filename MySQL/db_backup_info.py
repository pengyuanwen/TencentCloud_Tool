#!/usr/bin/python
# -*- coding: UTF-8 -*-
#author : yuanwen.peng
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import urllib
from QcloudApi.qcloudapi import QcloudApi
import MySQLdb
import datetime

now = datetime.datetime.now()
zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,microseconds=now.microsecond)
lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)


class Qcloud_api(object):

    def __init__(self):
        self.module = 'cdb'
        self.action = 'DescribeBackups'
        self.config = {'Region': 'ap-guangzhou',
                       'secretId': '',
                       'secretKey': '',
                       'mothod': 'GET',
                       'SignatureMethod': 'HmacSHA256',
                       'Version': '2017-03-20',
                       'cdbInstanceType': 1
                       }

        self.all_backup = []

    def get_backup_info(self,host_re):

        for item in host_re:
            project_name = item[0]
            sid = item[1]

            self.params = {'instanceId': sid
                           }

            service = QcloudApi(self.module, self.config)
            total = service.call(self.action, self.params)
            backup_info = json.loads(total)["data"]["items"][0]
            backup_name = backup_info["name"]
            format_backup_name = urllib.unquote(str(backup_name))
            backup_status = backup_info["status"]
            backup_start_time = backup_info["date"]
            backup_end_time = backup_info["finishTime"]
            backup_internetUrl = backup_info["internetUrl"]
            backup_intranetUrl = backup_info["intranetUrl"]
            backup_mode = backup_info["type"]
            backup_size = backup_info["size"]

            backup = (project_name,format_backup_name, backup_status, backup_start_time, backup_end_time, backup_internetUrl,
                  backup_intranetUrl, backup_mode, backup_size)
            self.all_backup.append(backup)
        return self.all_backup

    def get_conn(self):
        try:
            self.conn = MySQLdb.connect(
                host = 'ip',
                port = 3306,
                user = 'user',
                passwd = 'passwd',
                db = '',
                charset = 'utf8'
            )
        except MySQLdb.Error,e:
            errormag = 'Connot connect to server\nERROR (%s): %s' %(e.args[0],e.args[1])
            print errormag
            sys,exit()

    def query_db(self,select_sql):
        cursor = self.conn.cursor()
        cursor.execute(select_sql)
        result = cursor.fetchall()
        self.conn.commit()
        return result

    def insert(self,insert_sql):
        cursor = self.conn.cursor()
        cursor.execute(insert_sql)
        self.conn.commit()
        cursor.close()

    def get_host(self):
        self.get_conn()
        sql = 'SELECT project_name,mainSID from qcloud_info.db_info where created >= \'%s\' and created <= \'%s\';' % (zeroToday, lastToday)
        host_re = self.query_db(sql)
        return host_re

    def deal_data(self,ret):
        #self.get_conn()
        for item in ret:
            project_name = item[0]
            backup_name = item[1]
            backup_status = item[2]
            start_time = item[3]
            end_time = item[4]
            internetUrl = item[5]
            intranetUrl = item[6]
            backup_type = item[7]
            backup_size = item[8]


            sql = 'insert into qcloud_info.backup_info(project_name,backup_name,backup_status,start_time,end_time,internetUrl,intranetUrl,backup_type,backup_size)' \
                  ' values (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')' % \
                  (project_name,backup_name,backup_status,start_time,end_time,internetUrl,intranetUrl,backup_type,round(float(backup_size)/1024/1024,2))
            #print sql
            self.insert(sql)

    def __del__(self):
        self.conn.close()


if __name__ == '__main__':
    ten = Qcloud_api()
    rehost = ten.get_host()
    a = ten.get_backup_info(rehost)
    ten.deal_data(a)

