#!/usr/bin/python
# -*- coding: UTF-8 -*-
#author：yuanwen.peng
#time : 2018-06-04
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from conf.Tencent_conf import Tencent_Api
from template.File_Hander import File_Read_Write

class Change_Main_Subordinate(Tencent_Api):

    def __init__(self):
        super(Change_Main_Subordinate,self).__init__()

    # 提升灾备为主(灾备为上海)
    def Change_sh_for_main(self):
        sh_all_job_id = []
        #地域选择为上海
        region = 'sh'
        self.config["Region"] = "ap-shanghai"
        self.Action = "SwitchDrInstanceToMain"
        #从配置文件获取上海的实例ID
        # 主实例和灾备实例对应关系（广州：上海）
        File_Opera = File_Read_Write(region)
        sh_dr_sid = File_Opera.read_file()
        sh_all_dr_sid = list(sh_dr_sid.split(','))


        for dr_sid in sh_all_dr_sid:
            self.action_param = {
                'instanceId': dr_sid    #上海实例
            }
            result = self.execute()
            db_info = result["data"]
            status = result["codeDesc"]
            job_id = db_info.get('asyncRequestId')
            sh_all_job_id.append(job_id)
            print "上海容灾SID: %s,提升为主实例：%s" % (dr_sid, status)

        #新增功能：将job_id写入文件
        with open('/home/yuanwen.peng/scripts/python/rongzai/all_job_id.txt', 'w') as f:
            f.write(",".join(sh_all_job_id) + '\n')

        print sh_all_job_id

    # 提升灾备为主，回切（灾备为广州）
    def Change_gz_for_main(self):
        gz_all_job_id = []
        # 地域选择为广州
        region = 'gz'
        self.config["Region"] = "ap-guangzhou"
        self.Action = "SwitchDrInstanceToMain"
        # 主实例和灾备实例对应关系（上海：广州）
        File_Opera = File_Read_Write(region)
        gz_dr_sid = File_Opera.read_file()
        sh_all_dr_sid = list(gz_dr_sid.split(','))

        for dr_sid in sh_all_dr_sid:

            self.action_param = {
                'instanceId': dr_sid  # 广州实例
            }
            result = self.execute()
            db_info = result["data"]
            status = result["codeDesc"]
            job_id = db_info.get('asyncRequestId')
            gz_all_job_id.append(job_id)
            print "广州SID: %s,提升为主实例：%s" % (dr_sid, status)

        #新增功能：将job_id写入文件
        with open('/home/yuanwen.peng/scripts/python/rongzai/all_job_id.txt', 'w') as f:
            f.write(",".join(gz_all_job_id) + '\n')

        print gz_all_job_id



if __name__ == '__main__':
    region_addr = sys.argv[1]
    Break_M_S = Change_Main_Subordinate()
    if region_addr == 'gz':
        # 提升灾备（上海）为主实例，并断开复制
        Break_M_S.Change_sh_for_main()
    elif region_addr == 'sh':
        # 提升灾备（广州）为主实例，并断开复制
        Break_M_S.Change_gz_for_main()
    else:
        print "参数输入错误"


