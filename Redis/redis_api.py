#!/usr/bin/python
# -*- coding: UTF-8 -*-
#author : yuanwen.peng
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json,datetime,os
from QcloudApi.qcloudapi import QcloudApi
from conf.Qcloud_API import Qcloud_redis
from conf.MySQL_API import DB_API
from conf.html import Html_API


class Redis_Info(Qcloud_redis):

    def __init__(self):
        super(Redis_Info,self).__init__()
        self.all_info = []

    def Get_Redis_Info(self):
        offset=[x for x in range(0,10)]
        for num in offset:
            self.params["offset"] = num
            service = QcloudApi(self.module, self.config)
            total = service.call(self.action, self.params)
            redis_info = json.loads(total)["data"]["redisSet"]
            if not redis_info:
                continue
            for single_redis in redis_info:
                redisName = single_redis.get("redisName")
                redisSid = single_redis.get("redisId")
                redisVip = single_redis.get('wanIp')
                redisPort = single_redis.get('port')
                redis_usage_size = single_redis.get('sizeUsed')
                redis_total_size = single_redis.get('size')
                res=(redisName,redisSid,redisVip,redisPort,redis_usage_size,redis_total_size)
                self.all_info.append(res)
        #return self.all_info

    def Wirte_MySQL(self):
        mysql = DB_API('ip')
        mysql.get_conn()
        for item in self.all_info:
            redisName=item[0]
            redisSid=item[1]
            redisVip=item[2]
            redisPort=item[3]
            redis_usage_size=item[4]
            redis_total_size=item[5]

            sql = 'insert into qcloud_info.redis_info(project_name,sid,ip,port,usage_size,total_size) values (\'%s\',\'%s\',\'%s\',%s,%s,%s)' % (redisName,redisSid,redisVip,redisPort,redis_usage_size,redis_total_size)
            mysql.insert(sql)


class Build_html(Html_API):

    def __init__(self):
        super(Html_API,self).__init__()
        self.html = Html_API.html

    def get_info(self):
        now = datetime.datetime.now()
        zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                             microseconds=now.microsecond)
        lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)
        mysql=DB_API('10.30.85.66')
        mysql.get_conn()
        #sql = 'select project_name,sid,ip,port,usage_size,total_size from qcloud_info.redis_info where created >="%s" and created <="%s";' % (zeroToday,lastToday)
        sql = 'select project_name,sid,ip,port,usage_size,total_size,round(usage_size/total_size*100,2) as usage_percent from qcloud_info.redis_info where created >="%s" and created <="%s" order by usage_percent desc;' % (zeroToday, lastToday)
        re = mysql.query_db(sql)
        return re

    def html_table(self):
        html = self.html
        result = self.get_info()
        for item in result:
            project_name=item[0]
            redisSid=item[1]
            redisVip=item[2]
            redis_usage_size=item[4]
            redis_total_size=item[5]
            #redis_percen=round(redis_usage_size/redis_total_size,2)*100
            redis_percen=item[6]
            color_memory_percen="#40E0D0"
            if redis_percen >=80 and redis_percen<90:
                color_memory_percen = "#DAA520"
            elif redis_percen >= 90 and redis_percen <= 95:
                color_memory_percen = "#DC143C"

            html += '''
            <tr>
                                 <td>%s</td>
                                 <td>%s</td>
                                 <td>%s</td>
                                 <td>%s</td>
                                 <td>%s</td>
                                 <td bgcolor="%s">%s</td>

                         </tr>
                                         ''' % (project_name,redisSid,redisVip,redis_usage_size,redis_total_size,color_memory_percen,redis_percen)


        return html

    def report(self):
        with open("/home/yuanwen.peng/scripts/python/redis/redis_info.html", 'w') as f:
            f.write(self.html_table())



if __name__=='__main__':
    redis=Redis_Info()
    redis.Get_Redis_Info()
    redis.Wirte_MySQL()
    make_html=Build_html()
    make_html.report()
    os.system('python /home/yuanwen.peng/scripts/python/redis/send_mail.py')
