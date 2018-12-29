#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging
import tornado.web
import time
import functools
import urlparse
import datetime

from tornado.web import HTTPError
from db import database
from utils.session import *
from urllib import urlencode

def datediff(beginDate, endDate):
    """计算时间相差天数，输入格式为：str"""
    format = "%Y-%m-%d %H:%M:%S"
    bd = datetime.datetime.strptime(beginDate, format)
    ed = datetime.datetime.strptime(endDate, format)
    oneday = datetime.timedelta(days=1)
    count = 0
    while bd.date() < ed.date():
        ed = ed - oneday
        count += 1
    return count

class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *argc, **argkw):
        super(BaseHandler, self).__init__(*argc, **argkw)
        self.session = Session(self.application.session_manager, self)

    @property
    def get_session(self):
        return self.session

    @property
    def db(self):
        return database.database.getDB()

    def auth(self):
        if not self.session:
            self.redirect('/login')

    @property
    def logging(self):
        logging.basicConfig(level=logging.WARN,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=os.path.join(os.path.dirname(__file__), "log") + "web.log",
                            filemode='w')
        return logging

    @property
    def user(self):
        if self.session.get("mobile"):
            return self.session['data']
        else:
            return None

    @property
    def admin(self):
        if self.session.get("name"):
            return self.session['data']
        else:
            return None

    def begin_frontend_session(self, mobile, password):
        self.logging.info(('start login', mobile, password))
        if not self.application.frontend_auth.login(mobile, password):
            print "login failed"
            return False
        self.logging.info(('login checked', mobile, password))

        now = time.strftime('%Y-%m-%d %H:%M:%S')
        ip = self.request.remote_ip
        user = self.db.tb_user_profile.find_one({'mobile': mobile}, {'pwd': 0, '_id': 0})
        if not user:
            print mobile
            return False

        # print user
        logininfos = user.get('login',[])
        print logininfos

        logins = []
        if logininfos:
            if isinstance(logininfos,list):
                login = logininfos[-1]
                lastlogin = login.get('time')
                lastbonus = login.get('bonus_state',0)
                day = datediff(lastlogin, now)
                print day
                if day > 1:
                    logindays=1
                    bonus = 1 #可领取
                elif day < 1:
                    logindays = int(user.get('logindays',0))
                    bonus = lastbonus
                else:
                    logindays = int(user.get('logindays',0))+1
                    if logindays > 7:
                        logindays = 0
                    bonus = 1
                print logindays,bonus
                logins.append({"ip":ip,"time":now,"bonus_state":bonus})
            elif isinstance(logininfos,dict):
                logins.append(logininfos)
                logindays = 0
        else:
            logins.append({"ip": ip, "time": now, "bonus_state": 1})
            logindays = 0

        print logininfos,logindays
        m=self.db.tb_user_profile.update({'mobile': mobile}, {'$set': {'status': 'online', "logindays":logindays, "login":logins[-10:]}})
        print m

        user['status'] = "online"
        user['logindays'] = logindays
        user['login'] = logins[-10:]

        print "==>",user
        try:
            self.session['name'] = user.get('nick')
            self.session['data'] = user
            self.session["mobile"] = mobile
            self.session.save()
        except Exception as e:
            print e
        return True

    def end_frontend_session(self):
        # id = self.get_secure_cookie("session_id")
        # print "end_frontend_session=",id
        # self.application.sessions.clear_session(id)

        print self.session
        if self.session is not None:
            uid = self.session['data']['userid']
            username = self.session['mobile']
            print uid,username
            self.db.tb_user_profile.update({'userid': uid}, {'$set': {'status': 'offline'}})
            self.application.frontend_auth.logout(username)
        self.session['mobile'] = None
        self.session.save()

    def begin_backend_session(self, name, password):
        self.logging.info(('start login', name, password))
        if not self.application.backend_auth.login(name, password):
            print "login failed"
            return False
        self.logging.info(('login checked', name, password))
        # now = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        ip = self.request.remote_ip
        user = self.db.tb_system_user.find_one({'userid': name}, {'passwd': 0, '_id': 0})
        logininfos = user.get('login',[])
        print "哈哈"
        print logininfos

        logininfos.append({"ip": ip, "time": now})

        self.db.tb_system_user.update({'userid': name}, {'$set': {'status': 'online',"login":logininfos[-10:]}})
        # admin = self.db.tb_system_user.find_one({'userid': name}, {'passwd': 0, '_id': 0})
        # data = admin
        # self.logging.info(('login', data))
        user['status'] = "online"
        user['login'] = logininfos[-10:]

        self.session['mobile'] = None
        self.session['data'] = user
        self.session["name"] = name
        self.session.save()
        return True

    def end_backend_session(self):
        # id = self.get_secure_cookie("session_id")
        # self.application.sessions.clear_session(id)
        if self.session is not None:
            uid = self.session['data']['userid']
            username = self.session['name']
            self.db.tb_system_user.update({'userid': uid}, {'$set': {'status': 'offline'}})
            self.application.backend_auth.logout(username)
        self.session['name'] = None
        self.session.save()

    @classmethod
    def authenticated(self, method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.session.get('mobile'):
                if self.request.method in ("GET", "HEAD"):
                    url = self.get_login_url()
                    if "?" not in url:
                        if urlparse.urlsplit(url).scheme:
                            next_url = self.request.full_url()
                        else:
                            next_url = self.request.uri
                        url += "?" + urlencode(dict(next=next_url))
                    self.redirect(url)
                    return
                raise HTTPError(403)

            return method(self, *args, **kwargs)

        return wrapper

    def get_admin_login_url(self):
        self.require_setting("admin_login_url", "@admin_authed")
        return self.application.settings["admin_login_url"]

    @classmethod
    def admin_authed(self, method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.session.get('name'):
                if self.request.method in ("GET", "HEAD"):
                    url = self.get_admin_login_url()
                    if "?" not in url:
                        if urlparse.urlsplit(url).scheme:
                            # if login url is absolute, make next absolute too
                            next_url = self.request.full_url()
                        else:
                            next_url = self.request.uri
                        url += "?" + urlencode(dict(next=next_url))
                    self.redirect(url)
                    return
                raise HTTPError(403)
            else:
                if self.session['data'].get("role", "") != "superadmin":
                    # raise HTTPError(403)
                    # self.redirect('/admin/login')
                    return
            return method(self, *args, **kwargs)

        return wrapper
