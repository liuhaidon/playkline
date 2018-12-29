#!/usr/bin/env python
# coding: UTF-8
import json
import logging
import time
import pymongo


from view import *
from db import database
from pymongo import MongoClient
from passlib.handlers.pbkdf2 import pbkdf2_sha512

def loginbonus():
    """载入连续登陆金币奖励数据"""
    db = database.database.getDB()

    f = file('json/loginbonus.json')
    p = json.load(f)
    for i in list(p):
        i['id'] = int(i['id'])
        print i
        result = db.loginbonus.find_one({"id": i['id']})
        if result:
            db.loginbonus.update({"id": i['id']}, {"$set": {"gold": i['gold'], "loginday": i['loginday']}})
        else:
            db.loginbonus.insert(i)


def goldpurchas():
    """金币购买数据"""
    db = database.database.getDB()

    f = file('json/goldpurchas.json')
    p = json.load(f)
    for i in list(p):
        i['id'] = int(i['id'])
        i['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
        print i
        result = db.goldpurchas.find_one({"id": i['id']})
        if result:
            db.goldpurchas.update({"id": i['id']}, {"$set": {"gold": i['gold'], "money": i['money'],
                                                             "time": time.strftime("%Y-%m-%d %H:%M:%S")}})
        else:
            db.goldpurchas.insert(i)


def klinepackagelist():
    """K线数据导入"""
    db = database.database.getDB()

    f = file('json/klinepackagelist.json')
    p = json.load(f)
    for i in list(p):
        i['id'] = int(i['id'])
        print i
        result = db.klinepackagelist.find_one({"id": i['id']})
        if result:
            db.klinepackagelist.update({"id": i['id']}, {"$set": {"daylist": i['daylist']}})
        else:
            db.klinepackagelist.insert(i)


def notice_info():
    """K线系统公告导入"""
    db = database.database.getDB()

    f = file('json/notice_info.json')
    p = json.load(f)
    for i in list(p):
        i['id'] = int(i['id'])
        print i
        result = db.notice_info.find_one({"id": i['id']})
        if result:
            db.notice_info.update({"id": i['id']}, {"$set": {"title": i['title'], "content": i['content']}})
        else:
            db.notice_info.insert(i)


def create_user():
    """创建用户"""
    correct = False
    db = database.database.getDB()
    while 1:
        phone = raw_input("phone: ")
        exist_user = db.user.find_one({"phone": phone})
        if exist_user:
            print "the phone %s is existed" % phone
        else:
            break
    user = []
    nick = raw_input("name:")
    while not correct:
        passwd = raw_input("password:")
        rpwd = raw_input("confirm password:")
        if passwd == rpwd:
            correct = True
            last = db.user.find().sort("userid", pymongo.DESCENDING).limit(1)
            userid = id_auto_increment(last, "userid")
            user = {
                'userid': userid,
                'nick': nick,  # 用户名
                'avatar': 1,  # 头像
                'gold': 2800,  # 金币数
                'integral': 100,  # 积分
                'gametimes': 0,  # 比赛次数
                'wintimes': 0,  # 赢得次数
                'logindays': 0,  # 连续登录天数
                'phone': phone,
                'passwd': passwd,
                'regtime': time.strftime('%Y-%m-%d', time.localtime(time.time())),  # 注册时间
            }
        else:
            print "password not correct,please input again"
    password_hash = pbkdf2_sha512.encrypt(user['passwd'])
    user['passwd'] = password_hash
    record = db.user.find_one({"userid": user['userid']})
    if record is not None:
        return False
    db.user.insert(user)

def update_user_pwd():
    """更新用户密码"""
    correct = False
    db = database.database.getDB()
    while 1:
        username = raw_input("username: ")
        exist_user = db.tb_user_profile.find_one({"userid": username})
        if exist_user:
            print "the user %s is existed" % (username)
            break

    while not correct:
        passwd = raw_input("password:")
        rpwd = raw_input("confirm password:")
        if passwd == rpwd:
            correct = True
            password_hash = pbkdf2_sha512.encrypt(passwd)
            db.tb_user_profile.update({"userid": username}, {"$set": {"passwd": password_hash}})
        else:
            print "password not correct,please input again"

def create_admin():
    """创建管理员账号"""
    correct = False
    db = database.database.getDB()
    while 1:
        admin_name = raw_input("admin name: ")
        exist_admin = db.tb_system_user.find_one({"userid": admin_name})
        if exist_admin:
            print "the Admin %s is existed" % admin_name
        else:
            break
    admin = []
    while not correct:
        passwd = raw_input("password:")
        pwd2 = raw_input("confirm password:")
        if passwd == pwd2:
            correct = True
            logging.warn("A admin registered,name is %s" % admin_name)
            last = db.tb_system_user.find()
            userid = id_auto_increment(last, "userid")
            admin = {
                "userid": userid,
                "name": admin_name,
                "passwd": passwd,
                "role": "superadmin",
                'regtime': time.strftime('%Y-%m-%d', time.localtime(time.time())),
            }
        else:
            print "password not correct,please input again"
    password_hash = pbkdf2_sha512.encrypt(admin['passwd'])
    admin['passwd'] = password_hash
    record = db.tb_system_user.find_one({"userid": admin['userid']})
    if record is not None:
        logging.warn("that Admin name %s had been registered" % admin_name)
        return False
    db.tb_system_user.insert(admin)

def remove_admin():
    """移除管理员账号"""
    db = database.database.getDB()
    db.tb_system_user.remove({"role": "superadmin"})
    logging.warn("admin user had been removed")

def update_admin_pwd():
    """更新管理员密码"""
    db = database.database.getDB()
    correct = False
    while not correct:
        name = raw_input("name:")
        passwd = raw_input("password:")
        pwd2 = raw_input("confirm password:")
        if passwd == pwd2:
            correct = True
            password_hash = pbkdf2_sha512.encrypt(passwd)
            db.tb_system_user.update_one({"userid": name}, {"$set": {"passwd": password_hash}})
        else:
            print "password not correct,please input again"


def import_user_profile(conn):
    if not conn:
        conn = MongoClient('127.0.0.1')
    srcdb= conn.get_database('kline')
    # srcdb.authenticate("admin","rss123")
    dstdb = conn.get_database('playkline')
    # dstdb.authenticate("admin","rss123")

    dstdb.tb_user_profile.remove()
    users = srcdb.user.find({"status":"online"},{"_id":0})
    for v in users:
        logins = []
        login = {}
        logininfo = v.get('login', None)
        # print logininfo
        if logininfo:
            if isinstance(logininfo, list):
                logins = logininfo
            else:
                login['ip'] = logininfo.get('ip',0)
                login['time'] = logininfo.get('time', 0)
                login['bonus_state'] = logininfo.get('reeceive_state', 0)
                logins.append(login)

        playtimes = int(v.get('gametimes',0))
        wintimes = float(v.get('wintimes'))
        if playtimes < 1:
            winrate = 0
        else:
            winrate = round((wintimes / float(playtimes) * 100), 1)

        passwd = pbkdf2_sha512.encrypt("rss123")
        u = {"userid": v.get("uid"), "nick": v.get("nick", v.get('uid')), "avatar": v.get("avatar"),
              "score": v.get("integral"),"gold": v.get("gold"),"playtimes": v.get("gametimes",0),
             "wintimes": v.get("wintimes",0), "passwd": passwd, "mobile": v.get("phone"),
             "email": v.get("email",""),"login": logins,"regtime": v.get("regtime"),"status": v.get("status"),
             "settings": v.get("setting"),"logindays":v.get("logindays",0),"winrate":winrate
             }
        print u
        dstdb.tb_user_profile.insert(u)

def import_system_user(conn):
    if not conn:
        conn = MongoClient('127.0.0.1')
    srcdb= conn.get_database('attalk')
    # srcdb.authenticate("admin","rss123")
    dstdb = conn.get_database('playkline')
    # dstdb.authenticate("admin","rss123")

    dstdb.tb_system_user.remove()
    users = srcdb.tb_system_user.find({"status":"online"},{"_id":0})
    for v in users:
        logins = []
        login = {}
        logininfo = v.get('login', None)
        # print logininfo
        if logininfo:
            if isinstance(logininfo, list):
                logins = logininfo
            else:
                login['ip'] = logininfo.get('ip',0)
                login['time'] = logininfo.get('time', 0)
                login['bonus_state'] = logininfo.get('reeceive_state', 0)
                logins.append(login)

        u = {"userid": v.get("userid"), "nick": v.get("realname", v.get('userid')), "avatar": v.get("avatar"),
              "role": v.get("role"),"brief": v.get("desc",""), "passwd": v.get("passwd"), "mobile": v.get("phone"),
             "email": v.get("email",""),"login": logins,"regtime": v.get("regtime"),"status": v.get("status"),
             }
        print u
        dstdb.tb_system_user.insert(u)

def import_notice_profile(conn):
    if not conn:
        conn = MongoClient('127.0.0.1')
    srcdb= conn.get_database('kline')
    # srcdb.authenticate("admin","rss123")
    dstdb = conn.get_database('playkline')
    # dstdb.authenticate("admin","rss123")

    dstdb.tb_notice_profile.remove()
    notices = srcdb.notice_info.find()
    for v in notices:
        print v
        u = {"userid": v.get("issueid","admin"), "time": v.get("issuetime"), "title": v.get("title"),
              "content": v.get("content"), "platform": v.get("platform", 0), "status": v.get("ispublic"),
             }
        print u
        dstdb.tb_notice_profile.insert(u)

def import_login_bonus(conn):
    if not conn:
        conn = MongoClient('127.0.0.1')
    srcdb= conn.get_database('kline')
    # srcdb.authenticate("admin","rss123")
    dstdb = conn.get_database('playkline')
    # dstdb.authenticate("admin","rss123")

    dstdb.tb_login_bonus.remove()
    bonuses = srcdb.loginbonus.find()
    for v in bonuses:
        print v
        u = {"userid": v.get("issueid","admin"), "time": v.get("issuetime",time.strftime("%Y-%m-%d %H:%M:%S")),
             "loginday": v.get("loginday"), "bonus": v.get("gold"), "unit": v.get("unit", 0), "status": v.get("status",0)
             }
        print u
        dstdb.tb_login_bonus.insert(u)

def import_shop_package(conn):
    if not conn:
        conn = MongoClient('127.0.0.1')
    srcdb= conn.get_database('kline')
    # srcdb.authenticate("admin","rss123")
    dstdb = conn.get_database('playkline')
    # dstdb.authenticate("admin","rss123")

    dstdb.tb_recharge_package.remove()
    packages = srcdb.goldpurchas.find()
    for v in packages:
        print v
        u = {"userid": v.get("issueid","admin"), "time": v.get("issuetime",time.strftime("%Y-%m-%d %H:%M:%S")),
             "gold": v.get("gold"), "money": v.get("money"), "buy": v.get("buy", 0), "status": v.get("status",0)
             }
        print u
        dstdb.tb_recharge_package.insert(u)

def import_feedback_profile(conn):
    if not conn:
        conn = MongoClient('127.0.0.1')
    srcdb= conn.get_database('kline')
    # srcdb.authenticate("admin","rss123")
    dstdb = conn.get_database('playkline')
    # dstdb.authenticate("admin","rss123")

    dstdb.tb_feedback_profile.remove()
    feedbacks = srcdb.feedback.find()
    for v in feedbacks:
        print v
        u = {"userid": v.get("uid","admin"), "time": v.get("time",time.strftime("%Y-%m-%d %H:%M:%S")),
             "content": v.get("content"), "title": v.get("name"), "contact": v.get("contact", 0), "status": v.get("status",0)
             }
        print u
        dstdb.tb_feedback_profile.insert(u)

def import_order_profile(conn):
    if not conn:
        conn = MongoClient('127.0.0.1')
    srcdb= conn.get_database('kline')
    # srcdb.authenticate("admin","rss123")
    dstdb = conn.get_database('playkline')
    # dstdb.authenticate("admin","rss123")

    dstdb.tb_order_profile.remove()
    orders = srcdb.transaction_record.find()
    for v in orders:
        print v
        u = {"userid": v.get("uid","admin"), "time": v.get("time",time.strftime("%Y-%m-%d %H:%M:%S")),
             "content": v.get("content"), "title": v.get("name"), "contact": v.get("contact", 0), "status": v.get("status",0)
             }
        print u
        dstdb.tb_order_profile.insert(u)

def import_kline_profile(conn):
    if not conn:
        conn = MongoClient('127.0.0.1')
    srcdb= conn.get_database('kline')
    # srcdb.authenticate("admin","rss123")
    dstdb = conn.get_database('playkline')
    # dstdb.authenticate("admin","rss123")

    dstdb.tb_kline_package.remove()
    packages = srcdb.klinepackagelist.find({},{"_id":0})
    for v in packages:
        print v
        # u = {"userid": v.get("uid","admin"), "time": v.get("time",time.strftime("%Y-%m-%d %H:%M:%S")),
        #      "content": v.get("content"), "title": v.get("name"), "contact": v.get("contact", 0), "status": v.get("status",0)
        #      }
        # print u
        dstdb.tb_kline_package.insert(v)

def import_robert_profile(conn):
    if not conn:
        conn = MongoClient('127.0.0.1')
    srcdb= conn.get_database('playkline')
    # srcdb.authenticate("admin","rss123")
    dstdb = conn.get_database('playkline')
    # dstdb.authenticate("admin","rss123")

    dstdb.tb_robert_profile.remove()
    mobiles = ["13509673370","13809673370","13609673370","13709673370","13309673370","13409673370"]
    nicknames = ["rokia", "penny", "sophie", "wiley", "donny", "sonny"]
    packages = srcdb.tb_user_profile.find({},{"_id":0})
    for v in packages:
        print v
        u = v
        u["mobile"] = mobiles.pop()
        u["passwd"] = pbkdf2_sha512.encrypt("rss123")
        u["nick"] = nicknames.pop()
        u["userid"] = u["nick"]
        dstdb.tb_robert_profile.insert(u)

def create_room_profile(conn):
    if not conn:
        conn = MongoClient('127.0.0.1')
    srcdb= conn.get_database('playkline')
    dstdb = conn.get_database('playkline')
    # dstdb.authenticate("admin","rss123")

    dstdb.tb_room_profile.remove()
    mode =[1,2]
    style=[1,2,3]
    for m in mode:
        for n in style:
            spaceid = "%02d%02d"%(m,n)
            for v in range(1024):
                roomid="%06d"%v
                u={"spaceid":spaceid,"roomid":roomid,"status":0,"players":[],"weight":1}
                print u
                dstdb.tb_room_profile.insert(u)

if __name__ == "__main__":
    # input("please input a method:")
    conn = MongoClient('127.0.0.1')
    # import_shop_package(conn)
    import_user_profile(conn)
    import_system_user(conn)
    import_shop_package(conn)
    import_kline_profile(conn)
    import_notice_profile(conn)
    import_login_bonus(conn)
    import_feedback_profile(conn)
    import_order_profile(conn)
    import_robert_profile(conn)
