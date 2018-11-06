#!/usr/bin/python
# -*- coding: UTF-8 -*-
#author：yuanwen.peng
#time : 2018-06-04
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
from conf.Tencent_conf import Tencent_Api


class Rebulid_Master_Slave(Tencent_Api):

    # 重新建立主从复制关系(上海-广州）
    def change_master_to_sh(self):
        sh_all_job_id = []
        self.Action = 'SwitchDrMasterRole'
        self.config["Region"] = "ap-shanghai"
        #广州：上海
        with open('/home/yuanwen.peng/scripts/python/rongzai/write_sid.txt','a+') as f:
            all_sh_sid_info = f.read().strip('\n')
            all_sh_sid_info = json.loads(all_sh_sid_info)


        for gz_sid,sh_sid in all_sh_sid_info.items():
            self.action_param = {
                'srcInfo.cdbUInstanceId': sh_sid,  #即将作为主实例
                'srcInfo.regionId': 4,
                'srcInfo.zoneId': 200002,
                'srcInfo.isOverrideRoot': 1,
                'dstInfo.cdbUInstanceId': gz_sid,  #即将作为灾备实例
                'dstInfo.regionId': 1,
                'dstInfo.zoneId': 100004
            }
            try:
                res = self.execute()
                status = res["codeDesc"]
                if status == "Success":
                    print "主实例(上海)：%s,容灾实例(广州)：%s,重建主从状态：%s" % (sh_sid, gz_sid, status)
                    sh_job_id = res["data"]["asyncRequestId"]
                    sh_all_job_id.append(str(sh_job_id))
            except ValueError as e:
                print e

        # 新增功能：将job_id写入文件
        with open('/home/yuanwen.peng/scripts/python/rongzai/all_switch_job_id.txt', 'w') as f:
            f.write(",".join(sh_all_job_id) + '\n')


        print sh_all_job_id

    # 重新建立主从复制关系(广州-上海）
    def change_master_to_gz(self):

        self.Action = 'SwitchDrMasterRole'
        self.config["Region"] = "ap-guangzhou"

        # 主实例和灾备实例对应关系（上海：广州）
        #all_gz_sid_info = {'cdb-0zyx9uyi':'cdb-0ltonzse'}
        gz_all_job_id = []
        with open('/home/yuanwen.peng/scripts/python/rongzai/write_sid.txt','a+') as f:
            all_gz_sid_info = f.read().strip('\n')
            all_gz_sid_info = json.loads(all_gz_sid_info)
        for sh_sid,gz_sid in all_gz_sid_info.items():
            print sh_sid,gz_sid

            self.action_param = {
                'srcInfo.cdbUInstanceId': gz_sid,  #即将作为主实例
                'srcInfo.regionId': 1,
                'srcInfo.zoneId': 100004,
                'srcInfo.isOverrideRoot': 1,
                'dstInfo.cdbUInstanceId': sh_sid,  #即将作为灾备实例
                'dstInfo.regionId': 4,
                'dstInfo.zoneId': 200002

            }

            try:
                res = self.execute()
                status = res["codeDesc"]
                if status == "Success":
                    print "主实例(广州)：%s,容灾实例(上海)：%s,重建主从状态：%s" % (gz_sid, sh_sid, status)
                    gz_job_id = res["data"]["asyncRequestId"]
                    gz_all_job_id.append(str(gz_job_id))
            except ValueError as e:
                print e

        # 新增功能：将job_id写入文件
        with open('/home/yuanwen.peng/scripts/python/rongzai/all_switch_job_id.txt', 'w') as f:
            f.write(",".join(gz_all_job_id) + '\n')

        print gz_all_job_id


if __name__ == '__main__':
    region_addr = sys.argv[1]
    Rebulid_M_S = Rebulid_Master_Slave()
    if region_addr == 'gz':
        # 上海提升为主库
        Rebulid_M_S.change_master_to_sh()
    elif region_addr == 'sh':
        # 广州提升为主库
        Rebulid_M_S.change_master_to_gz()
    else:
        print "参数输入错误"

