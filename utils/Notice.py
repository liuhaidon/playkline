# encoding:utf-8
import json
import logging
import os
import urllib
import urllib2
import time
from db import database
from utils import Singleton
from BaseHandler import BaseHandler

log_path = os.path.join(os.getcwd(), "log")

log_filename = os.path.join(log_path, "warn.log")
if not os.path.exists(log_filename):
    if os.path.isdir("./log"):
        pass
    else:
        os.mkdir("./log")
    f = open(log_filename, 'w')
    f.close()

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=log_filename,
                    filemode='w')


class Notice(Singleton):
    """站内通知
        tpye:消息类型
        level:消息级别
        tpl_id:短消息模板id
        timeout:超时未读取发送短信通知
    """

    def __int__(self):
        self.timeout = 60 * 60 * 24

    @property
    def db(self):
        return database.database.getDB()
