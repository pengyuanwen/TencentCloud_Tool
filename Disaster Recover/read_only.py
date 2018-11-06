#!/usr/bin/python
# -*- coding: UTF-8 -*-
#author：yuanwen.peng
#time : 2018-06-04
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from conf.Tencent_conf import Tencent_Api
from template.File_Hander import File_Read_Write



class Read_Only(Tencent_Api):

    def __init__(self):
        super(Read_Only,self).__init__()
        # 切换前主实例的实例ID(广州）
        self.all_gz_master_sid = File_Read_Write('gz').read_file().split(',')
        # 切换前主实例的实例ID(上海）
        self.all_sh_master_sid = File_Read_Write('sh').read_file().split(',')


    def gz_read_only(self):

        for master_id in self.all_gz_master_sid:
            self.action_param = {'instanceId': master_id, 'readOnly': 1}
            result = self.execute()
            status = result["codeDesc"]
            print "广州主实例SID:%s,开启read_only:%s" % (master_id, status)


    # 主库开启只读（上海）
    def sh_read_only(self):

        self.config["Region"] = "ap-shanghai"
        for master_id in self.all_sh_master_sid:
            self.action_param = {'instanceId': master_id, 'readOnly': 1}
            result = self.execute()
            status = result["codeDesc"]
            print "上海主实例SID:%s,开启read_only:%s" % (master_id, status)


if __name__ == '__main__':
    region_addr = sys.argv[1]
    open=Read_Only()
    if region_addr == 'gz':
        #广州开启只读
        open.gz_read_only()
    elif region_addr == 'sh':
        #上海开启只读
       open.sh_read_only()
    else:
        print "参数输入错误"
