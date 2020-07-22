#!/usr/bin/python
# -*- coding: UTF-8 -*-
#author : yuanwen.peng
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import MySQLdb
import datetime
import time


now = datetime.datetime.now()
zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,microseconds=now.microsecond)
lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)



class DB_API(object):

    def __init__(self,host):
        self.host = host

        self.all_db = []

        self.all_host_info = []

        self.all_res = []

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

    def query_db(self,select_sql):
        query_cursor = self.conn.cursor()
        query_cursor.execute(select_sql)
        query_result = query_cursor.fetchall()
        self.conn.commit()
        return query_result
        #self.all_db_tab.append(query_result)



    def insert_db(self,sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def __del__(self):
        self.conn.close()

    def get_all_host(self):

        sql = 'SELECT project_name,mainip from qcloud_info.db_info where created >= \'%s\' and created <= \'%s\' limit 100;' % (zeroToday,lastToday)
        host_res = self.query_db(sql)
        for i in host_res:
            project_name = i[0]
            host_ip = i[1]
            host_info = (project_name,host_ip)
            self.all_host_info.append(host_info)
        return self.all_host_info


    def get_db_info(self):

        db_sql = 'show databases;'
        re = self.query_db(db_sql)
        res = list(re)
        db = [x[0] for x in res]
        mysql_db = ['mysql', 'information_schema', 'performance_schema', 'sys', 'test']
        create_db = list(set(db) - set(mysql_db))
        self.all_db.append(create_db)
        return self.all_db


    def get_parti_info(self):

        for db in self.all_db[0]:

            partition_sql = 'SELECT t1.table_schema,t1.table_name,max(SUBSTR(t1.partition_name,2)) partition_name,max(t1.PARTITION_DESCRIPTION) PARTITION_DESCRIPTION ' \
                            'FROM information_schema.PARTITIONS t1,information_schema.tables t2 ' \
                            'WHERE t1.TABLE_SCHEMA=t2.TABLE_SCHEMA ' \
                            'AND t1.table_name=t2.table_name ' \
                            'AND t1.table_schema= \'%s\' ' \
                            'AND t1.PARTITION_DESCRIPTION is not null ' \
                            'GROUP BY t1.table_schema,t1.table_name;' % (db)

            handle_res = self.query_db(partition_sql)
            if handle_res:
                self.all_res.append(handle_res)
        return self.all_res





class out_put_line(object):

    def __init__(self):
        self.finall = []

    def get_all_info(self):
        mysql = DB_API('ip')
        mysql.get_conn()
        info = mysql.get_all_host()
        #print info
        return info

    def query_mysql(self,sql):
        mysql_conn = DB_API('ip')
        mysql_conn.get_conn()
        re = mysql_conn.query_db(sql)

        return re[0][0]


    def write_mysql(self,sql):
        mysql_conn = DB_API('ip')
        mysql_conn.get_conn()
        mysql_conn.insert_db(sql)


    def get_part_info(self,ret):
        for item in ret:
            projectname = item[0]
            hostname = item[1]
            all_db = DB_API(hostname)
            all_db.get_conn()
            all_db.get_db_info()
            all_part_info = all_db.get_parti_info()

            #print all_part_info
            if not len(all_part_info):
                dbname = 0
                table_name = 0
                max_partition = 0
                max_part_time = 0
                format_part_time = 0

                insert_sql = 'insert into qcloud_info.partition_info(project_name,ip,dbname,table_name,max_partition,max_partition_time,expired_time) values (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',%s,%s);' % (projectname,hostname,dbname,table_name,max_partition,max_part_time,format_part_time)
                
                self.write_mysql(insert_sql)
                print insert_sql


            else:
                for i in all_part_info:
                    for j in i:
                        dbname = j[0]
                        table_name = j[1]
                        max_partition = j[2]
                        max_part_time = j[3]
                        #format_part_time = j[4]
                        if len(max_part_time) > 8 and max_part_time.isalnum():

                            timeArray = time.localtime(int(max_part_time))
                            expired_time = time.strftime("%Y%m%d", timeArray)
                            insert_sql = 'insert into qcloud_info.partition_info(project_name,ip,dbname,table_name,max_partition,max_partition_time,expired_time) ' \
                                         'values (\'%s\',\'%s\',\'%s\',\'%s\',\'p%s\',%s,%s);' % \
                                         (projectname, hostname, dbname, table_name, max_partition, max_part_time, expired_time)
                            print insert_sql
                            self.write_mysql(insert_sql)

                        elif len(max_part_time) < 7:
                            day_sql = 'select from_days(%s);' % max_part_time
                            _max_part_time = self.query_mysql(day_sql)

                            insert_sql = 'insert into qcloud_info.partition_info(project_name,ip,dbname,table_name,max_partition,max_partition_time,expired_time) ' \
                                         'values (\'%s\',\'%s\',\'%s\',\'%s\',\'p%s\',\'%s\',\'%s\');' % \
                                         (projectname, hostname, dbname, table_name, max_partition, max_part_time,_max_part_time)
                            print insert_sql
                            self.write_mysql(insert_sql)


                        else:
                            max_part_time = max_part_time.strip('\'')
                            insert_sql = 'insert into qcloud_info.partition_info(project_name,ip,dbname,table_name,max_partition,max_partition_time,expired_time) ' \
                                         'values (\'%s\',\'%s\',\'%s\',\'%s\',\'p%s\',\'%s\',\'%s\');' % \
                                         (projectname, hostname, dbname, table_name, max_partition, max_part_time, max_part_time)
                            print insert_sql
                            self.write_mysql(insert_sql)





if __name__ == '__main__':
    handle = out_put_line()
    re = handle.get_all_info()
    handle.get_part_info(re)

