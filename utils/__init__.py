#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import urllib
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')

class Singleton(object):
    """单例"""

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


def send_short_msg(tpl_id='1218461', tpl_value="#code#=123456", mobile_number='13360503305'):
    url = 'http://yunpian.com/v1/sms/tpl_send.json'
    values = {'apikey': '6eabf224a8e2d0b7092b663f1e55ba2e',
              'mobile': mobile_number,
              'tpl_id': tpl_id,
              'tpl_value': tpl_value,
              }
    print values
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()

def SendSMS(verification='121846', mobile='13360503305', tpl=u"【玩转K线】您的验证码是{0}。如非本人操作，请忽略本短信。"):
    print verification,mobile,tpl

    url = 'https://sms.yunpian.com/v2/sms/single_send.json'
    content = tpl.format(verification)
    print content
    values = {'apikey': '6eabf224a8e2d0b7092b663f1e55ba2e',
              'mobile': mobile,
              'text': content,
              }
    print values
    try:
        data = urllib.urlencode(values)
        print "data=", data
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        # print "response=",response
    except Exception as e:
        print "ex=", e
        error = {"code": 1, "msg": "短信发送异常！"}
        return error

    return response.read()