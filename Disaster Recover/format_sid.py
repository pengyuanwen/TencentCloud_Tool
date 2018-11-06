#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author:yuanwen.peng
#time:2018-06-12
import sys,pymysql
reload(sys)
sys.setdefaultencoding('utf-8')
from template.MySQL_API import DB_API
from template.File_Hander import File_Read_Write



region = sys.argv[1]

class Data_Hander(object):

    def __init__(self):
        self.MySQL = DB_API('ip')
        self.File_Hander = File_Read_Write(region)
        self.re_all = []

    @property
    def format_sid(self):
        self.MySQL.get_conn()
        if region == 'gz':
            gz = self.File_Hander.read_file()

            #广州-上海
            for i in gz.split(','):
                try:
                    select_sql = 'select drSID from qcloud_info.db_info where masterSID in (\'%s\') and drSID is not null limit 1;' % (i)
                    re = self.MySQL.query(select_sql)
                    a = (i, re[0][0])
                    self.re_all.append(a)
                except Exception,e:
                    print "实例名所在地区与输入地区不符，请重新输入。"

            self.File_Hander.write_file(dict(self.re_all))
        #
        elif region == 'sh':
            sh = self.File_Hander.read_file()
            # 上海-广州
            for i in sh.split(','):
                #ip = i.strip('\n')
                try:
                    select_sql = 'select masterSID from qcloud_info.db_info where drSID in (\'%s\') limit 1;' % (i)
                    re = self.MySQL.query(select_sql)
                    a = (i, re[0][0])
                    self.re_all.append(a)
                except Exception,e:
                    print "实例名所在地区与输入地区不符，请重新输入。"

            self.File_Hander.write_file(dict(self.re_all))
        print self.re_all
        return dict(self.re_all)



if __name__ == '__main__':
  re=Data_Hander()
  re.format_sid



