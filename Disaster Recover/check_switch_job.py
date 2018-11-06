#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author：yuanwen.peng
# time : 2018-06-04
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from conf.Tencent_conf import Tencent_Api

class Check_Swith_Job(Tencent_Api):

    def __init__(self):
        super(Check_Swith_Job,self).__init__()

    # 检查复制是否重新建立（上海-广州）
    def check_switch_sh_job(self):
        self.config["Region"] = "ap-shanghai"
        self.Action = 'DescribeRequestResult'

        #新增功能自动获取switch_job_id
        with open('/home/yuanwen.peng/scripts/python/rongzai/all_switch_job_id.txt', 'r') as f:
            all_job_id = f.read().strip('\n')
            _sh_all_job_id = all_job_id.split(',')



        for job_id in _sh_all_job_id:
            self.action_param = {
                'asyncRequestId': job_id
            }
            res = self.execute()
            print res

            status = res["codeDesc"]
            begin_time = res["data"]["startTime"]
            end_time = res["data"]["endTime"]
            print "任务ID：%s,Switch 状态：%s，切换开始时间：%s，切换完成结束时间：%s" % (job_id, status, begin_time, end_time)


    # 检查复制是否重新建立（广州-上海）
    def check_switch_gz_job(self):
        self.config["Region"] = "ap-guangzhou"
        self.Action = 'DescribeRequestResult'

        # 新增功能自动获取switch_job_id
        with open('/home/yuanwen.peng/scripts/python/rongzai/all_switch_job_id.txt', 'r') as f:
            all_job_id = f.read().strip('\n')
            _gz_all_job_id = all_job_id.split(',')


        for job_id in _gz_all_job_id:

            self.action_param = {
                'asyncRequestId': job_id
            }
            res = self.execute()
            status = res["codeDesc"]
            begin_time = res["data"]["startTime"]
            end_time = res["data"]["endTime"]
            print "任务ID：%s,Switch 状态：%s，切换开始时间：%s，切换完成结束时间：%s" % (job_id, status, begin_time, end_time)


if __name__ == '__main__':
    Check_Swith_Job = Check_Swith_Job()
    region_addr = sys.argv[1]
    if region_addr == 'gz':
        # 检查复制是否建立成功（上海-广州）
        Check_Swith_Job.check_switch_sh_job()
    elif region_addr == 'sh':
        # 检查复制是否建立成功（广州-上海）
        Check_Swith_Job.check_switch_gz_job()
    else:
        print "参数输入错误"
