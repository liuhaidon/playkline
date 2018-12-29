#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import random
import string


def id_auto_increment(last, id):
    """id自增1"""
    if last.count() > 0:
        lastone = dict()
        for item in last:
            lastone = item
        return int(lastone[id]) + 1
    else:
        return 1


def strtodatetime(datestr, format):
    return datetime.datetime.strptime(datestr, format)


def datediff(beginDate, endDate):
    """计算时间相差天数，输入格式为：str"""
    format = "%Y-%m-%d %H:%M:%S"
    bd = strtodatetime(beginDate, format)
    ed = strtodatetime(endDate, format)
    oneday = datetime.timedelta(days=1)
    count = 0
    while bd.date() < ed.date():
        ed = ed - oneday
        count += 1
    return count


def random_number(length):
    """生成随机位数字符"""
    # seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"
    seed = "01234567890"
    sa = []
    for i in range(length):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    return salt
