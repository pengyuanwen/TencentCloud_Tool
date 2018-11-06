#!/usr/bin/python
# -*- coding: utf-8 -*-
#author : yuanwen.peng
import os
def output_result():
    os.system("python /home/yuanwen.peng/scripts/python/Qcloud/Qcloud_api_1.py")
    os.system("python /home/yuanwen.peng/scripts/python/Qcloud/db_backup_info.py")
    os.system("python /home/yuanwen.peng/scripts/python/Qcloud/backup_info_html.py")
    os.system("python /home/yuanwen.peng/scripts/python/Qcloud/send_mail.py")

output_result()
