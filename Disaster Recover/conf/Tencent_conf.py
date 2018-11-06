#!/usr/bin/python
# -*- coding: UTF-8 -*-
#author：yuanwen.peng
#time : 2018-06-04

import json
from QcloudApi.qcloudapi import QcloudApi
class Tencent_Api(object):

    def __init__(self):
        self.module = 'cdb'
        self.Action = 'ModifyDBInstanceReadOnlyStatus'
        self.config = {'Region': 'ap-guangzhou',
                       'secretId': '',
                       'secretKey': '',
                       'mothod': 'GET',
                       'SignatureMethod': 'HmacSHA256',
                       'Version': '2017-03-20'
                       }
        self.action_param = {}


    def execute(self):

        service = QcloudApi(self.module, self.config)
        reslut = service.call(self.Action, self.action_param)
        db_info = json.loads(reslut)
        print reslut
        return db_info


