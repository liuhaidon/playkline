#!/usr/bin/env python
# coding: UTF-8
import json
import logging
import re
import time
import datetime

from fabric.api import run, env, cd
import os
from fabric.operations import get
from passlib.handlers.pbkdf2 import pbkdf2_sha512

from db import database

env.hosts = ['root@112.74.133.196:22']
env.password = 'vchits@2016'


def test():
    "test"
    run('ls -l /webapps')


def zipdb():
    """
    打包服务器数据文件
    mongodb:kline
    """
    with cd('/root/work/mongo'):
        run('zip kline_mongodb.zip kline.ns kline.0')


def getzipdb():
    """下载服务器用户上传图片资源文件
    本地存储路径：'../zip/' """
    with cd('/root/work/mongo'):
        get('kline_mongodb.zip', 'zip/')


def zipimage():
    """打包服务器图片资源文件
    """
    with cd('/webapps/web_kline/static'):
        run('tar czvf static.tar.gz css img js')


def getimagezip():
    """下载服务器用户上传图片资源文件
    本地存储路径：'../zip/' """
    with cd('/webapps/web_kline/static'):
        get('web_kline.tar.gz', 'zip/')


def test_deploy():
    """测试前后端部署:
    测试端口：7000
    python Main.py --port=7000
    """
    # TODO
    with cd('/webapps/web_kline'):
        run('git reset --hard HEAD')
        run('git pull -f web_kline master')
        run('sudo supervisorctl restart web_kline')


def restart_web():
    """重启web进程"""
    # TODO
    with cd('/webapps/web_kline'):
        run('sudo supervisorctl stop web_kline')
        run('sudo supervisorctl restart web_kline')


def front_deploy():
    """前端代码部署"""
    # TODO
    with cd('/webapps/web_kline'):
        run('sudo supervisorctl stop web_kline')
        run('sudo supervisorctl restart web_kline')


def back_deploy():
    """前后端代码部署"""
    # TODO
    # 部署
    with cd('/webapps/web_kline'):
        run('git reset --hard HEAD')
        run('git pull -f web_kline master')
        run('sudo supervisorctl restart web_kline')
        # run('sudo supervisorctl restart tornadoes:*')


def back_deploy2():
    """前后端代码部署 https"""
    # TODO
    # 部署
    with cd('/webapps/web_kline'):
        run('git reset --hard HEAD')
        run('git pull -f web_kline_https master')
        run('sudo supervisorctl restart web_kline')


def restart_celery():
    """重启计时任务"""
    # TODO
    with cd('/webapps/web_kline'):
        run('sudo supervisorctl restart celeryd')


# def check_online():
#     """检查股权计划状态"""
#     db = database.database.getDB()
#     db.interest.update(
#         {"status": "preheating", "start_date": {"$lte": datetime.datetime.now()}},
#         {"$set": {"status": "online"}},
#         upsert=True)


def push_rollback():
    """远程服务器代码回滚
    git 回滚到上一个版本
    """
    # TODO


def reload_mongodb():
    """重启mongodb"""
    run("sudo service mongod reload")


def css_compress(css_file="/webapps/kline/static/css/merge.css"):
    """css压缩"""
    f = open(css_file, "a+")
    css = str(f.readlines())
    ignorePattern = re.compile(r'\s*\:\s*', re.IGNORECASE)
    css = ignorePattern.sub(':', css)

    ignorePattern = re.compile(r';?\s*\}\s*', re.IGNORECASE)
    css = ignorePattern.sub('}', css)

    ignorePattern = re.compile(r'\s*\{\s*', re.IGNORECASE)
    css = ignorePattern.sub('{', css)

    ignorePattern = re.compile(r'\s{2,}', re.IGNORECASE)
    css = ignorePattern.sub(' ', css)

    ignorePattern = re.compile(r'/\*[\s\S]*?\*/', re.IGNORECASE)
    css = ignorePattern.sub('', css)
    print>> f, css
    f.close()


def test_screen():
    """切到挂起的screen"""
    run('screen -d -r kline')
