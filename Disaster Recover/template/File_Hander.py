#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author:yuanwen.peng
#time:2018-06-12

import sys,json
reload(sys)
sys.setdefaultencoding('utf-8')


class File_Read_Write(object):

    def __init__(self,region):
        self.region = region

    def read_file(self):
        if self.region == 'gz':
            with open('/home/yuanwen.peng/scripts/python/rongzai/gz_sid.txt', 'a+') as f:

                return f.read().strip('\n')
        elif self.region == 'sh':
            with open('/home/yuanwen.peng/scripts/python/rongzai/sh_sid.txt', 'a+') as f:
                return f.read().strip('\n')



    def write_file(self,ret):
        with open('/home/yuanwen.peng/scripts/python/rongzai/write_sid.txt', 'w') as f:
            f.writelines(json.dumps(dict(ret)) + '\n')



