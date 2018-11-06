#!/usr/bin/python
# -*- coding: UTF-8 -*-
#author：yuanwen.peng
#time : 2018-06-04
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
from QcloudApi.qcloudapi import QcloudApi
from conf.Tencent_conf import Tencent_Api
from template.File_Hander import File_Read_Write

class Check_Job(Tencent_Api):

    def check_sh_job(self):

        sh_all_sid_list = []
        region = 'sh'
        self.Action='DescribeRequestResult'
        self.config["Region"] = "ap-shanghai"

        #新增自动获取job_id
        with open('/home/yuanwen.peng/scripts/python/rongzai/all_job_id.txt', 'r') as f:
            all_job_id = f.read().strip('\n')
            sh_all_job_id = all_job_id.split(',')


        for job_id in sh_all_job_id:

            self.action_param={
                'asyncRequestId': job_id
            }
            restule = self.execute()
            #print restule
            status = restule["codeDesc"]
            master_info = restule["data"]["data"][0]["masterInfo"]["instanceId"]
            dr_info = restule["data"]["data"][0]["drInfo"]["instanceId"]
            sid_info = (master_info, dr_info)
            sh_all_sid_list.append(sid_info)
            print "任务ID:%s，上海容灾提升为主实例状态：%s，广州实例ID: %s，上海实例ID: %s" % (job_id,status,master_info,dr_info)
        #主实例和容灾实例对于关系，以方便下一步重新构造复制（广州，上海）
        File_Oper = File_Read_Write(region)
        File_Oper.write_file(sh_all_sid_list)
        print sh_all_sid_list


    def check_gz_job(self):
        gz_all_sid_list = []
        region = 'gz'
        self.Action = 'DescribeRequestResult'
        self.config["Region"] = "ap-guangzhou"

        #新增功能自动获取job_id
        with open('/home/yuanwen.peng/scripts/python/rongzai/all_job_id.txt', 'r') as f:
            all_job_id = f.read().strip('\n')
            gz_all_job_id = all_job_id.split(',')



        for job_id in gz_all_job_id:
            self.action_param = {
                'asyncRequestId': job_id
            }
            restule = self.execute()
            status = restule["codeDesc"]
            master_info = restule["data"]["data"][0]["masterInfo"]["instanceId"]
            dr_info = restule["data"]["data"][0]["drInfo"]["instanceId"]
            sid_info = (master_info, dr_info)
            gz_all_sid_list.append(sid_info)
            print "任务ID:%s，广州容灾提升为主实例状态：%s，上海实例ID: %s，广州实例ID: %s" % (job_id, status, master_info, dr_info)
        # 主实例和容灾实例对于关系，以方便下一步重新构造复制（广州，上海）
        File_Oper = File_Read_Write(region)
        File_Oper.write_file(gz_all_sid_list)
        print gz_all_sid_list





if __name__ == '__main__':
    Check_Break_Job = Check_Job()
    region_addr = sys.argv[1]
    if region_addr == 'gz':
        # 检查灾备(上海)提升为主是否成功
        Check_Break_Job.check_sh_job()
    elif region_addr == 'sh':
        #检查灾备(广州)提升为主是否成功
        Check_Break_Job.check_gz_job()
    else:
        print "参数输入错误"
