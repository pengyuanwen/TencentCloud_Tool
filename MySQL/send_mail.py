#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Zabbix SMTP Alert script from idreamsky.
"""
import sys,datetime
import smtplib
from email.mime.text import MIMEText
now_time = datetime.datetime.now().strftime('%Y-%m-%d')
#邮件发送列表，发给哪些人
mailto_list="xxxx@idreamsky.com"
sub = "Qcloud_DB_Backup_Report %s" % now_time
#设置服务器，用户名、口令以及邮箱的后缀
mail_host="xxxx.com"
mail_user="xxx"
mail_pass="xxx"
mail_postfix="xxx.com"
#定义send_mail函数
def send_mail(to_list,sub):

    with open('/home/yuanwen.peng/scripts/python/Qcloud/backupinfo.html','rb+') as file:
        mail_body = file.read()
    '''
    to_list:发给谁
    sub:主题
    content:内容
    send_mail("lvs071103@qq.com","sub","content")
    '''
    address=mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(mail_body, _subtype='html', _charset='utf-8')
    #msg = MIMEText(content,_subtype='html', _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = address
    msg['To'] = to_list
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        #s.starttls()
        s.login(mail_user,mail_pass)
        s.sendmail(address, to_list.split(','),msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False
if __name__ == '__main__':
        send_mail(mailto_list,sub)