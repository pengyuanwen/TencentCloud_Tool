#!/usr/bin/python
# -*- coding: UTF-8 -*-
#author:yuanwen.peng
class Qcloud_redis(object):

    def __init__(self):
        self.module = 'redis'
        self.action = 'DescribeRedis'
        self.config = {'Region': 'ap-guangzhou',
                       'secretId': '',
                       'secretKey': '',
                       'mothod': 'GET',
                       'SignatureMethod': 'HmacSHA256',
                       'version': '2017-03-12'
                       }
        self.params = {'limit': 100,
                       'offset': 0}