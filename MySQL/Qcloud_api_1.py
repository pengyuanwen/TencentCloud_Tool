#!/usr/bin/python
# -*- coding: UTF-8 -*-
#author : yuanwen.peng
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
from QcloudApi.qcloudapi import QcloudApi
#import xlrd
#import xlwt
import MySQLdb
import datetime

class Qcloud_api(object):

        def __init__(self):
            self.module='cdb'
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
                           'offset': 0,
                           }
            #主实例信息
            self.all_info = []
            #灾备实例信息
            self.dr_info = []
            #所有实例信息
            self.all_db_info = []

        #得到主实例信息
        def All_Instance_Info(self):

            self.config['InstanceTypes.N'] = 1
            action_Instance = 'DescribeCdbInstances'
            service = QcloudApi(self.module, self.config)
            total = service.call(action_Instance, self.params)
            total_Count = json.loads(total)['totalCount']

						#判断一共有多少页
            if total_Count >= int(self.params['limit']):
                page_num = total_Count / int(self.params['limit'])
                if total_Count % int(self.params['limit']) != 0:
                    page_num = page_num + 1
            else:
                page_num = 1

            for i in range(page_num):
                self.params['offset'] = int(self.params['limit'])*i
                total = service.call(action_Instance, self.params)
                db_info = json.loads(total)["cdbInstanceSet"]

                for item in db_info:
                    sid = item.get('uInstanceId')
                    sid_name = item.get('cdbInstanceName')
                    master_ip = item.get('cdbInstanceVip')
                    slave_info = item.get('roInfo')
                    dr_info = item.get('drInfo')
                    disk_info = item.get('volume')
                    master_sid = item.get("cdbInstanceType")

                    if master_sid == 3:
                        pass
                    else:
                        if not slave_info:
                            slave_info = '0'
                            slave_sid = slave_info
                            slave_ip = slave_info
                        else:
                            slave_sid = slave_info[0].get('uInstanceId')
                            slave_ip = slave_info[0].get('vip')

                        if not dr_info:
                            dr_info = '0'
                            dr_sid = dr_info
                        else:
                            dr_sid = dr_info[0].get('uInstanceId')

                        self.all_info.append([sid_name, sid, master_ip, slave_sid, slave_ip, dr_sid, disk_info])

        #灾备实例信息
        def Dr_Info(self):
            self.config['cdbInstanceType'] = '2'
            self.config['Region'] = 'ap-shanghai'
            self.params.pop('offset')
            dr_action_Instance = 'DescribeCdbInstances'
            dr_service = QcloudApi(self.module, self.config)
            total = dr_service.call(dr_action_Instance, self.params)
            dr_db_info = json.loads(total)["cdbInstanceSet"]

            for dr in dr_db_info:

                dr_sid = dr['uInstanceId']
                dr_ip = dr['cdbInstanceVip']
                dr_status = dr['cdbInstanceType']
                if dr_status == 2:
                    self.dr_info.append([dr_sid,dr_ip])


        #磁盘使用率
        def Check_Disk(self):
            for i in self.all_info:
                master_sid = i[1]
                monitor_module = 'monitor'
                monitor_action = 'GetMonitorData'
                metricName = ['real_capacity','volume_rate']

                for metric in metricName:
                    monitor_params = {'namespace': 'qce/cdb',
                                           'dimensions.0.name': 'uInstanceId',
                                           'dimensions.0.value': master_sid,
                                           'metricName': metric,
                                           'period': 60 / 300
                                           }

                    nomitor_service = QcloudApi(monitor_module, self.config)
                    monitor_total = nomitor_service.call(monitor_action, monitor_params)
                    #print monitor_total
                    monitor_db_info = json.loads(monitor_total)["dataPoints"]
                    #print monitor_db_info
                    res = monitor_db_info[-2]
                    #print res
                    #if isinstance(res,int):
                    disk_userd = round(res/1024,2)
                    i.append(disk_userd)

            #print self.all_info



        #处理结果
        def OutPut_Result(self):
            self.All_Instance_Info()
            self.Check_Disk()
            self.Dr_Info()
            for all in self.all_info:

                if all[5] == '0':
                    all.append('0')
                    continue
                for dr in self.dr_info:
                    if all[5] == dr[0]:
                        all.append(dr[1])
            return self.all_info
  


        #写数据到excle
        # def write_excle(self):
        #
        #     wb = xlwt.Workbook(encoding='utf-8')
        #     ws = wb.add_sheet('db info', cell_overwrite_ok=True)
        #     ws.write(0, 0, '项目名称')
        #     ws.write(0, 1, '主实例ID')
        #     ws.write(0, 2, '主实例IP')
        #     ws.write(0, 3, '从实例ID')
        #     ws.write(0, 4, '从实例IP')
        #     ws.write(0, 5, '灾备实例ID')
        #     ws.write(0, 6, '灾备实例IP')
        #
        #     row_begin = 1
        #     for i in self.all_info:
        #         col_begin = 0
        #         for j in i:
        #             ws.write(row_begin, col_begin, j)
        #             col_begin += 1
        #         row_begin += 1
        #     wb.save('D:\python\\1.xls')


class DB_API(object):

    def __init__(self,host,ret):
        self.host = host
        self.ret =ret

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

    def deal_data(self):
       # print self.ret
        self.get_conn()

        for i in self.ret:
            project_name = i[0]
            masterSID = i[1]
            masterIP = i[2]
            slaveSID = i[3]
            slaveIP = i[4]
            drSID = i[5]
            disk_total = i[6]
            disk_usage = i[7]
            disk_percent = i[8] * 1000
            drIP = i[9]
            sql = 'insert into qcloud_info.db_info(project_name,masterSID,masterIP,slaveSID,slaveIP,drSID,drIP,disk_total,disk_usage,disk_percent) values (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',%s,%s,\'%s\');'\
                  % (project_name, masterSID, masterIP, slaveSID, slaveIP, drSID, drIP,disk_total,disk_usage,(disk_usage/disk_total)*100)
            print sql
            self.insert(sql)

        now = datetime.datetime.now()
        days_seven_ago = now + datetime.timedelta(days=-7)
        zeroSevenday_ago = days_seven_ago - datetime.timedelta(hours=days_seven_ago.hour, minutes=days_seven_ago.minute, seconds=days_seven_ago.second,microseconds=days_seven_ago.microsecond)
        lastSevenday_ago = zeroSevenday_ago + datetime.timedelta(hours=23, minutes=59, seconds=59)

        delete_sql = 'delete from qcloud_info.db_info where created <= "%s";' % (lastSevenday_ago)
        #print delete_sql
        self.insert(delete_sql)


    def __del__(self):
        self.conn.close()

if __name__ == '__main__':
    Ten = Qcloud_api()
    ret = Ten.OutPut_Result()
    MySQL = DB_API('ip',ret)
    MySQL.deal_data()










