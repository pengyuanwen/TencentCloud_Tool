#!/usr/bin/python
# -*- coding: UTF-8 -*-
#author:yuanwen.peng

class Html_API(object):

    html = '''
            <!DOCTYPE html> 
            <html>
            <head>
            <meta charset="utf-8">
            <title>腾讯云Redis信息</title>
            </head>
            <body>

            <table border="1"  bgcolor="#40E0D0">
            <tr>
              <th>项目名称</th>
              <th>实例ID</th>
              <th>实例IP地址</th>
              <th>内存已使用大小(M)</th>
              <th>内存总大小(M)</th>
              <th>内存使用百分比</th>
            </tr> '''