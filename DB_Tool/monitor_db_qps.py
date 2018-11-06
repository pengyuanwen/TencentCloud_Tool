#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import json, datetime
import smtplib
import pymysql
from QcloudApi.qcloudapi import QcloudApi
from operator import itemgetter
from email.mime.text import MIMEText


class Datetime_Format(object):
    def __init__(self):
        pass

    @staticmethod
    def NowTimeInit():
        now = datetime.datetime.now()
        str_date = now.strftime('%Y-%m-%d %H:%M:%S')
        return str_date

    @staticmethod
    def EndTimeInit():
        endtime = datetime.datetime.strptime(Datetime_Format.NowTimeInit(), '%Y-%m-%d %H:%M:%S')

        return endtime

    @staticmethod
    def StartTimeInit():
        now_starttime = Datetime_Format.EndTimeInit() + datetime.timedelta(hours=-1)
        return now_starttime

    #修复当天凌晨数据为空的bug，每次获取前一天的实例列表信息
    @staticmethod
    def NowDayBegin():
        now_day = datetime.datetime.strptime(Datetime_Format.NowTimeInit(),'%Y-%m-%d %H:%M:%S')
        yesterday = now_day + datetime.timedelta(days=-1)
        str_yesterday = yesterday.strftime('%Y-%m-%d %H:%M:%S')
        yes_day_begin = str_yesterday[:10] + ' ' + '00:00:00'
        #print yes_day_begin
        return yes_day_begin

    # 修复当天凌晨数据为空的bug，每次获取前一天的实例列表信息
    @staticmethod
    def NowDayEnd():
        # now_day = Datetime_Format.NowTimeInit()
        # now_day_end = now_day[:10] + ' ' + '23:59:59'
        # return now_day_end
        now_day = datetime.datetime.strptime(Datetime_Format.NowTimeInit(), '%Y-%m-%d %H:%M:%S')
        yesterday = now_day + datetime.timedelta(days=-1)
        str_yesterday = yesterday.strftime('%Y-%m-%d %H:%M:%S')
        now_day_end = str_yesterday[:10] + ' ' + '23:59:59'
        return now_day_end


class SqlInit(object):
    cqb_sid = 'select project_name,masterSID,masterIP from qcloud_info.db_info where created >= \'%s\' and  created <= \'%s\';' % (
    Datetime_Format.NowDayBegin(), Datetime_Format.NowDayEnd())

    cqb_redis = 'select project_name,sid,ip from qcloud_info.redis_info where created >=\'%s\' and  created <=\'%s\';' % (
    Datetime_Format.NowDayBegin(), Datetime_Format.NowDayEnd())


class Qcloud_api(object):
    def __init__(self):
        self.module = 'cdb'
        self.action = 'DescribeCdbInstances'
        self.config = {'Region': 'ap-guangzhou',
                       'secretId': '',
                       'secretKey': '',
                       'mothod': 'GET',
                       'SignatureMethod': 'HmacSHA256',
                       'version': '2017-03-12',
                       'cdbInstanceType': 1
                       }

        self.params = {'limit': 100,
                       'offset': 0}

        self.db = DB('ip', 3306, 'user', 'passwd', 'dbname')

        self.startTime = Datetime_Format.StartTimeInit()
        self.endTime = Datetime_Format.EndTimeInit()
        self.cdb_info = []
        self.redis_info = []

    def cdb_qps(self):

        self.db.get_conn()
        res = self.db.query(SqlInit.cqb_sid, None)
        for item in res:

            projectname = item[0]
            master_sid = item[1]
            sidip = item[2]
            monitor_module = 'monitor'
            monitor_action = 'GetMonitorData'
            # metricName = ['qps','tps']
            metricName = ['qps']

            for metric in metricName:
                monitor_params = {'namespace': 'qce/cdb',
                                  'dimensions.0.name': 'uInstanceId',
                                  'dimensions.0.value': master_sid,
                                  'metricName': metric,
                                  'startTime': self.startTime,
                                  'endTime': self.endTime
                                  # 'period': 60/300
                                  }

                nomitor_service = QcloudApi(monitor_module, self.config)
                monitor_total = nomitor_service.call(monitor_action, monitor_params)

                monitor_db_info = json.loads(monitor_total)["dataPoints"]
                res = (projectname, master_sid, sidip, round(max(monitor_db_info)))
                self.cdb_info.append(res)

        return self.cdb_info

    def redis_qps(self):

        self.module = 'redis'
        self.db.get_conn()
        res = self.db.query(SqlInit.cqb_redis, None)

        for item in res:
            projectname = item[0]
            master_sid = item[1]
            sidip = item[2]

            monitor_module = 'monitor'
            monitor_action = 'GetMonitorData'
            metricName = ['qps']
            for metric in metricName:
                monitor_params = {'namespace': 'qce/redis',
                                  'dimensions.0.name': 'redis_uuid',
                                  'dimensions.0.value': master_sid,
                                  'metricName': metric,
                                  'startTime': self.startTime,
                                  'endTime': self.endTime

                                  }
                nomitor_service = QcloudApi(monitor_module, self.config)
                monitor_total = nomitor_service.call(monitor_action, monitor_params)
                monitor_db_info = json.loads(monitor_total)["dataPoints"]

                res = (projectname, master_sid, sidip, round(max(monitor_db_info)))
                self.redis_info.append(res)
        #print self.redis_info
        return self.redis_info


class DB(object):
    def __init__(self, db_host, db_port, db_user, db_passwd, db_name):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_passwd = db_passwd
        self.db_name = db_name

    def get_conn(self):
        try:
            self.conn = pymysql.Connect(
                host=self.db_host,
                port=int(self.db_port),
                user=self.db_user,
                passwd=self.db_passwd,
                db=self.db_name,
                charset='utf8'
                # cursorclass = pymysql.cursors.DictCursor
            )
        except pymysql.Error as e:
            print e
            exit(11)

    def query(self, sql, val):
        cursor = self.conn.cursor()
        cursor.execute(sql, val)
        result = cursor.fetchall()
        cursor.close()
        return result

    def update(self, sql, val):
        cursor = self.conn.cursor()
        cursor.execute(sql, val)
        self.conn.commit()
        cursor.close()

    def __del__(self):
        if self.db_host is not None or self.db_port is not None:
            # if self.conn is not None:
            self.conn.close()


class HandleData(object):
    html_head = '''
                    <!DOCTYPE html> 
                    <html>
                    <head>
                    <meta charset="utf-8">
                    <title>腾讯云QPS信息</title>
                    </head>
                    <style>
                        .qps{
                                color: red;
                            }
                    </style>
                    <body>

    
    '''


    html_cdb = '''


                    <table border="1"  bgcolor="#40E0D0">
                    <tr>
                      <th>项目名称</th>
                      <th>数据库实例</th>
                      <th>数据库IP</th>
                      <th>每小时最大QPS数量</th>


                    </tr> '''
    html_redis = '''


                    <table border="1"  bgcolor="#40E0D0">
                    <tr>
                      <th>项目名称</th>
                      <th>数据库实例</th>
                      <th>数据库IP</th>
                      <th>每小时最大QPS数量</th>


                    </tr> '''

    def __init__(self):
        pass

    @staticmethod
    def Qcloud_Init():
        return Qcloud_api()

    @staticmethod
    def BulidCqbData():
        Qcloud = HandleData.Qcloud_Init()
        res_cdb = Qcloud.cdb_qps()
        return sorted(res_cdb, key=itemgetter(3), reverse=True)

    @staticmethod
    def BuildRedisData():
        Qcloud = HandleData.Qcloud_Init()
        res_redis = Qcloud.redis_qps()
        return sorted(res_redis, key=itemgetter(3), reverse=True)

    @staticmethod
    def BulidCqbHtml():
        res = HandleData.BulidCqbData()
        for item in res:
            project_name = item[0]
            sidname = item[1]
            sidip = item[2]
            cdb_qps = item[3]

            HandleData.html_cdb += """
                                 <tr>
                                 <td>%s</td>
                                 <td>%s</td>
                                 <td>%s</td>
                                 <td>%s</td>
                                 </tr>
            """ % (project_name, sidname, sidip, cdb_qps)
        reshtml = HandleData.html_head + HandleData.html_cdb
        return reshtml

    @staticmethod
    def BuildRedisHtml():
        res = HandleData.BuildRedisData()
        for item in res:
            project_name = item[0]
            sidname = item[1]
            sidip = item[2]
            redis_qps = item[3]
            HandleData.html_redis += """
                                             <tr>
                                             <td>%s</td>
                                             <td>%s</td>
                                             <td>%s</td>
                                             <td>%s</td>
                                             </tr>
                        """ % (project_name, sidname, sidip, redis_qps)

        reshtml = HandleData.html_head + HandleData.html_redis
        return reshtml

    def report_cdb(self):
        with open("/home/yuanwen.peng/scripts/python/Qcloud/cdbqps_info.html", 'w') as f:
            f.write(HandleData.BulidCqbHtml())

    def report_Redis(self):
        with open("/home/yuanwen.peng/scripts/python/Qcloud/redisqps_info.html", 'w') as f1:
            f1.write(HandleData.BuildRedisHtml())


class Mail(object):
    def __init__(self, mailto_list):
        self.mailto_list = mailto_list
        self.mail_host = "xxx.com"
        self.mail_user = "xxx"
        self.mail_pass = "xxx"
        self.mail_postfix = "xxx.com"

    def SendToCdb(self):
        Handledata = HandleData()
        Handledata.report_cdb()
        with open('/home/yuanwen.peng/scripts/python/Qcloud/cdbqps_info.html', 'rb+') as file:
            mail_body = file.read()
        address = self.mail_user + "<" + self.mail_user + "@" + self.mail_postfix + ">"
        msg = MIMEText(mail_body, _subtype='html', _charset='utf-8')
        msg['Subject'] = self.sub
        msg['From'] = address
        msg['To'] = self.mailto_list
        try:
            s = smtplib.SMTP()
            s.connect(self.mail_host)
            # s.starttls()
            s.login(self.mail_user, self.mail_pass)
            s.sendmail(address, self.mailto_list.split(','), msg.as_string())
            s.close()
            return True
        except Exception, e:
            print str(e)
            return False

    @staticmethod
    def CqbMess():
        Handledata = HandleData()
        Handledata.report_cdb()
        with open('/home/yuanwen.peng/scripts/python/Qcloud/cdbqps_info.html', 'rb+') as file:
            mail_body = file.read()
        return mail_body

    @staticmethod
    def RedisMess():
        Handledata = HandleData()
        Handledata.report_Redis()
        with open('/home/yuanwen.peng/scripts/python/Qcloud/redisqps_info.html', 'rb+') as file:
            mail_body = file.read()
        return mail_body

    def MailMes(self, mail_body, type):
        if type == "cqb":
            receive = "MySQL QPS".encode('utf-8')
            _sub = "%s-%s" % (Datetime_Format.StartTimeInit(),Datetime_Format.EndTimeInit())
        elif type == "redis":
            receive = "Redis QPS".encode('utf-8')
            _sub = "%s-%s" % (Datetime_Format.StartTimeInit(),Datetime_Format.EndTimeInit())
        else:
            exit(1);

        #address = self.mail_user + "<" + self.mail_user + "@" + self.mail_postfix + ">"
        address = receive + "<" + self.mail_user + "@" + self.mail_postfix + ">"
        msg = MIMEText(mail_body, _subtype='html', _charset='utf-8')
        msg['Subject'] = _sub
        msg['From'] = address
        msg['To'] = self.mailto_list
        try:
            s = smtplib.SMTP()
            s.connect(self.mail_host)
            # s.starttls()
            s.login(self.mail_user, self.mail_pass)
            s.sendmail(address, self.mailto_list.split(','), msg.as_string())
            s.close()
            return True
        except Exception, e:
            print str(e)
            return False


if __name__ == '__main__':
    mailto_list = "xxxx.com"
    Mail = Mail(mailto_list)
    Mail.MailMes(Mail.CqbMess(), 'cqb')
    Mail.MailMes(Mail.RedisMess(), 'redis')


