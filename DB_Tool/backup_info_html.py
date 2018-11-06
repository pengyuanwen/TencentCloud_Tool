#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author : yuanwen.peng
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import MySQLdb
import datetime


class DB_API(object):

    def __init__(self,host):
        self.host = host

    def get_conn(self):
        try:
            self.conn = MySQLdb.connect(
                host = self.host,
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

    def query(self,select_sql):
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

    def __del__(self):
        self.conn.close()

    def get_backuo_info(self):
        now = datetime.datetime.now()
        zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                             microseconds=now.microsecond)
        lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)

        #sql = 'select project_name,backup_name,start_time,end_time,backup_status,backup_type,backup_size from qcloud.backup_info;'
        sql = 'select t1.project_name,t1.backup_name,t1.start_time,t1.end_time,(TIME_TO_SEC(end_time) - TIME_TO_SEC(start_time))/60  cost_time,t1.backup_status,t1.backup_type,t1.backup_size,t2.disk_usage,t2.disk_total,t2.disk_percent from qcloud_info.backup_info t1 left join qcloud_info.db_info t2 on t1.project_name = t2.project_name where t1.created >= "%s" and t1.created <= "%s" and t2.created >= "%s" and t2.created <="%s" order by backup_status,disk_percent desc;' % (zeroToday,lastToday,zeroToday,lastToday)
        re = self.query(sql)
        return re

    def html_test(self):
        res = self.get_backuo_info()



        html = '''
        <!DOCTYPE html> 
        <html>
        <head>
        <meta charset="utf-8">
        <title>腾讯云备份信息</title>
        </head>
        <body>


        <table border="1"  bgcolor="#40E0D0">
        <tr>
          <th>项目名称</th>
          <th>备份集名称</th>
          <th>备份开始时间</th>
          <th>备份结束时间</th>
          <th>备份所花费时间(分)</th>
          <th>备份状态</th>
          <th>备份类型</th>
          <th>备份大小</th>
          <th>磁盘使用大小(G)</th>
          <th>磁盘总大小(G)</th>
          <th>磁盘使用率</th>

        </tr> '''

        for i in res:
            project_name = i[0]
            backup_name = i[1]
            start_time = i[2]
            end_time = i[3]
            cost_time = i[4]
            backup_status = i[5]
            backup_type = i[6]
            backup_size = i[7]
            disk_usage = i[8]
            disk_total = i[9]
            disk_percent = i[10]

            bak_bgcolor = "#40E0D0"
            bak_size_bgcolor = "#40E0D0"
            usage_per_color = "#40E0D0"
            disk_percent_color = "#40E0D0"

            # if int(disk_percent) < 1:
            #     usage_per_color = "#DC143C"
            if backup_status !='SUCCESS':
                bak_bgcolor = '#DC143C'
            if backup_size == 0:
                bak_size_bgcolor = "#DC143C"
            if int(disk_percent) >= 85:
                disk_percent_color = '#DC143C'

            '''
            add Change
            '''
            if len(str(int(backup_size))) < 4:
                backup_size = '%sM' % bytes(backup_size)
            elif  len(str(int(backup_size))) >= 4:
                backup_size = '%sG' % bytes(round(backup_size/1024,2))




            html += '''
                     <tr>
                                 <td>%s</td>
                                 <td>%s</td>
                                 <td>%s</td>
                                 <td>%s</td>
                                 <td>%s</td>
                                 <td bgcolor="%s">%s</td>
                                 <td>%s</td>
                                 <td bgcolor="%s">%s</td>
                                 <td>%s</td>
                                 <td>%s</td>
                                 <td bgcolor="%s">%s</td>
                         </tr>
                                         ''' % (project_name, backup_name, start_time, end_time, cost_time,bak_bgcolor, backup_status, backup_type, bak_size_bgcolor, backup_size,disk_usage, disk_total,disk_percent_color,disk_percent)





        return html

    def report(self):
        with open("/home/yuanwen.peng/scripts/python/Qcloud/backupinfo.html", 'w') as f:
            f.write(self.html_test())


a=DB_API('ip')
a.get_conn()
b = a.report()



