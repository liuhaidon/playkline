# encoding:utf-8

import time
import pymongo
import json

from tornado.web import HTTPError
from BaseHandler import BaseHandler
from view import *
from bson import DBRef, ObjectId
from passlib.hash import pbkdf2_sha512

class AdminLoginHandler(BaseHandler):
    """登录"""
    def get(self):
        # tornado.web.RequestHandler._template_loaders.clear()
        nexts = self.request.arguments.get("next")
        referer_url = '/admin/home'
        if 'Referer' in self.request.headers:
            referer_url = '/' + '/'.join(self.request.headers['Referer'].split("/")[3:])
        error = ""
        if self.admin:
            print self.admin
            if self.admin.get("role", "") in ['admin', "superadmin"]:
                print self.admin.get("role", "role is xxx")
                self.redirect(referer_url)
                error = ""
            else:
                error = "您已登录账号:%s,如继续则退出当前账号" % self.admin['name']

        next = referer_url
        if nexts:
            next = nexts[0]
        else:
            url = ""
        self.render("backend/login.html", url=next, error=error)

    def post(self, *args, **kwargs):
        print self.request.arguments
        self.logging.info(('LoginHandler argument %s') % (self.request.arguments))
        # print [value[0] for key, value in self.request.arguments.items() if key != '_xsrf']
        url, pwd, name = (value[0] for key, value in self.request.arguments.items() if key != '_xsrf'
                          and key != 'checkbox')
        if not pwd:
            self.render("backend/login.html", url=url, error="密码不能为空")
        self.logging.info(('admin user  %s login in' % (name)))

        print url,pwd,name
        res = self.begin_backend_session(name, pwd)
        if not res:
            self.render("backend/login.html", url=url, error="用户名或密码不正确")

        # # 登录记录
        # get_ip = self.request.remote_ip
        # self.db.logininfo.insert({"name": self.admin['name'], "ip": get_ip, "time": time.strftime("%Y-%m-%d %H:%M:%S")})
        print "url==>",url
        if url == '/admin/login':
            self.redirect('/admin/home')
        else:
            self.redirect(url)


class AdminLogoutHandler(BaseHandler):
    """注销"""

    def get(self):
        self.post()

    def post(self):
        self.end_backend_session()
        self.redirect('/admin/login')


class AdminHomeHandler(BaseHandler):
    """后台主页"""
    # @BaseHandler.admin_authed
    def get(self):
        print "进入首页"
        self.render("backend/home.html", myuser=self.admin, admin_nav=0)


class AdminUserList(BaseHandler):
    """用户列表"""
    # @BaseHandler.admin_authed
    def get(self):
        print "进来啦"
        user_list = self.db.tb_user_profile.find().sort("regtime", pymongo.DESCENDING)
        print user_list
        self.render("backend/user_list.html", myuser=self.admin, admin_nav=21, users=user_list)

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.tb_user_profile.remove({"userid": ObjectId(value[0])})
        return self.write(json.dumps({"status": "success", "error": "", "msg": u'删除用户成功'}))

class AdminSysUsers(BaseHandler):
    """用户列表"""
    # @BaseHandler.admin_authed
    def get(self):
        user_list = self.db.tb_system_user.find().sort("time", pymongo.DESCENDING)
        print user_list
        self.render("backend/system_user_query.html", myuser=self.admin, admin_nav=22, users=user_list)

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.tb_system_user.remove({"userid": ObjectId(value[0])})
        return self.write(json.dumps({"status": "success", "error": "", "msg": u'删除用户成功'}))


class AdminSysUserAdd(BaseHandler):
    """添加用户"""
    # @BaseHandler.admin_authed
    def post(self):
        userid = self.get_argument("userid", None)
        pwd = self.get_argument("passwd", None)

        nickname = self.get_argument('nickname', None)
        role = self.get_argument("role", "admin")
        brief = self.get_argument('brief', None)

        email = self.get_argument('email', None)
        mobile = self.get_argument('mobile', None)

        print email, mobile, userid, pwd, role
        user = self.db.tb_system_user.find_one({'userid': userid})
        if user:
            self.logging.info(u'该帐号已经注册')
            return self.write(json.dumps({"msg": u'该帐号已经注册', "status": 'error'}))

        img_arr = ['1.jpg', '3.jpg', '3.jpg', '2.jpg', '7.jpg', '8.jpg', '5.jpg', '6.jpg']
        user = {
            'userid': userid,
            'passwd': pwd,
            'nickname': nickname,
            'role': role,
            'brief': brief,
            'regtime': time.strftime("%Y-%m-%d %H:%M:%S"),
            'mobile': mobile,
            'email': email,
            'avatar': random.choice(img_arr),
        }

        print 'user=%s' % user
        res = self.application.backend_auth.register(user)
        print "auth res=>", res
        if res:
            print "register error"
            return self.write(json.dumps({"msg": u'增加系统用户失败', "status": 'error'}))
        return self.write(json.dumps({"msg": u'增加系统用户成功', "status": 'success'}))


class AdminDeleteSysUser(BaseHandler):
    """删除后端用户"""
    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        print datas
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.tb_system_user.remove({"_id": ObjectId(value[0])})
        self.write(json.dumps({"status": 'ok', "msg": u'删除成功'}))


class AdminModifySysUser(BaseHandler):
    """修改后端用户"""
    # @BaseHandler.admin_authed
    def get(self, id):
        print "libraryid=", id
        record = self.db.tb_system_user.find_one({"_id": ObjectId(id)})
        print id, record
        # print "question==>", type(record.get('questions', []))
        return self.render("backend/system_user_modify.html", myuser=self.admin, admin_nav=22, sysuser=record)

    # @BaseHandler.admin_authed
    def post(self, id):
        print "userid=", id
        record = self.db.tb_system_user.find_one({"_id": ObjectId(id)})
        print record
        if not record:
            return self.write(json.dumps({"status": 'error', "msg": "修改的后端用户不存在！"}))
        newprofile = {
            'userid': self.get_argument("userid"),
            'nickname': self.get_argument("nickname"),
            'mobile': self.get_argument("mobile"),
            'email': self.get_argument("email"),
            'role': self.get_argument("role"),
            'regtime': self.get_argument("regtime"),
            'status': self.get_argument("status"),
        }

        for k, v in newprofile.iteritems():
            if not v:
                return self.write(json.dumps({"status": 'error', "msg": k + "为必选项，请输入信息！"}))

        newprofile["brief"] = self.get_argument("brief")
        newprofile["passwd"] = record.get("passwd")
        newprofile["avatar"] = record.get("avatar")
        newprofile["login"] = record.get("login")

        print "new record==>", newprofile
        m = self.db.tb_system_user.update_one({"_id": record.get('_id')}, {"$set": newprofile})
        return self.write(json.dumps({"status": 'ok', "msg": "修改的后端用户成功！"}))


class AdminRepassSystem(BaseHandler):
    """删除密码"""
    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments

        pass3 = self.get_argument("password3", None)
        pass4 = self.get_argument("password4", None)
        if pass3 != pass4:
            return self.write(json.dumps({"status": 'error', "msg": "确认密码跟新密码不一致！"}))

        userid = self.get_argument("storeid", None)
        pass3 = pbkdf2_sha512.encrypt(pass3)

        m = self.db.tb_system_user.update_one({"_id": ObjectId(userid)}, {"$set": {"passwd":pass3}})
        self.write(json.dumps({"status": 'ok', "msg": u'修改密码成功'}))


class AdminUserAdd(BaseHandler):
    """添加用户"""
    
    # @BaseHandler.admin_authed
    def get(self):
        users = self.db.tb_user_profile.find({"role": {"$ne": 'superadmin'}})
        type = self.get_argument("type", None)
        role = self.get_argument("role", None)
        # nav = {"0": 21, "jury": 22, "scientist": 23, "investor": 24, "gm": 25}
        tags = self.db.iptag.find()
        print "sssssssssssssssss"
        self.render("backend/add_user.html", myuser=self.admin, admin_nav=22, type=type, tags=tags, users=users)

    # @BaseHandler.admin_authed
    def post(self):
        username = self.get_argument("username", None)
        email = self.get_argument('email', None)
        phone = self.get_argument('phone', None)

        pwd = self.get_argument("pwd", None)
        role = self.get_argument("role", "")
        user = self.db.tb_user_profile.find_one({'uid': username})
        area = self.request.arguments.get("area")
        print area
        if user:
            self.logging.info(u'该帐号已经注册')
            return self.write(json.dumps({"msg": u'该帐号已经注册', "error": 'error'}))
        else:
            # baseurl = "http://cdn.zi-han.net/im/temp/"
            img_arr = ['1.jpg', '3.jpg', '3.jpg', '2.jpg', '7.jpg', '8.jpg', '5.jpg', '6.jpg']
            user = {
                'userid': username,
                'passwd': pwd,
                'name': username,
                'role': role,
                'regtime': time.strftime('%Y-%m-%d', time.localtime(time.time())),
                'phone': phone,
                'email': email,
                'avatar': random.choice(img_arr),
                'pay_pwd': pwd,  # 支付密码，默认与登录密码一样
            }
            if area:
                user.update({"area": area})
            # print 'user%s'%user
            self.logging.info(('register user %s %s' % (user['uid'], user['pwd'])))
            res = self.application.auth.register(user)
            if not res:
                print "register error"
                return self.write(json.dumps({"msg": u'注册失败', "error": 'error'}))
        self.redirect('/admin/users')



class AdminNoticeList(BaseHandler):
    """系统公告列表"""
    # @BaseHandler.admin_authed
    def get(self):
        notice_info = self.db.tb_notice_profile.find({"status": 1}).sort("atime", pymongo.ASCENDING)
        self.render("backend/notice_list.html", myuser=self.admin, admin_nav=61, notices=notice_info)


class AdminAddNotice(BaseHandler):
    """发布公告"""
    # @BaseHandler.admin_authed
    def get(self):
        self.render("backend/notice_add.html", myuser=self.admin, admin_nav=3)

    # @BaseHandler.admin_authed
    def post(self):
        info = dict()
        info['title'] = self.get_argument('title')
        info['content'] = self.get_argument('content')
        info['userid'] = self.admin['userid']
        info['status'] = 1
        info['platform'] = 0
        info['atime'] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.db.tb_notice_profile.insert(info)
        return self.write(json.dumps({"status": "ok", "msg": u'增加系统公告成功'}))

class AdminDeleteNotice(BaseHandler):
    """删除公告"""
    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.tb_notice_profile.remove({"_id": ObjectId(value[0])})
        self.write(json.dumps({"status": 'ok'}))


class AdminModifyNotice(BaseHandler):
    """修改公告"""
    @BaseHandler.admin_authed
    def get(self, id):
        record = self.db.tb_notice_profile.find_one({"_id": ObjectId(id)})
        self.render("backend/notice_modify.html", myuser=self.admin, admin_nav=91, notice=record)

    @BaseHandler.admin_authed
    def post(self, noticeid):
        print "noticeid=", noticeid
        record = self.db.tb_notice_profile.find_one({"_id": ObjectId(noticeid)})
        print record
        if not record:
            return self.write(json.dumps({"status": 'error', "msg": "修改的公告不存在！"}))

        newprofile = {
            'title': self.get_argument("title", None),
            'content': self.get_argument("content", None),
            'userid': self.get_argument("userid", None),
            'atime': self.get_argument("atime", None),
        }
        for k, v in newprofile.iteritems():
            if not v:
                return self.write(json.dumps({"status": 'error', "msg": k + "为必选项，请输入信息！"}))

        newprofile['status'] = self.get_argument("status", 1)

        m = self.db.tb_notice_profile.update({"_id": record.get('_id')}, {"$set": newprofile})
        print m

        return self.write(json.dumps({"status": 'ok', "msg": "修改公告成功！"}))


class AdminFeedbackList(BaseHandler):
    """用户反馈列表"""

    # @BaseHandler.admin_authed
    def get(self):
        feedbacks = self.db.tb_feedback_profile.find().sort("_id", pymongo.DESCENDING)
        self.render("backend/feedback_list.html", myuser=self.admin, admin_nav=71, feedbacks=feedbacks)

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.tb_feedback_profile.remove({"_id": ObjectId(value[0])})
        return self.write(json.dumps({"status": "ok", "msg": u'删除反馈信息成功'}))

class AdminAddFeedback(BaseHandler):
    """发布反馈"""

    # @BaseHandler.admin_authed
    def get(self):
        self.render("backend/notice_add.html", myuser=self.admin, admin_nav=3)

    # @BaseHandler.admin_authed
    def post(self):
        self.request.arguments
        info = dict()
        info['title'] = self.get_argument('title')
        info['content'] = self.get_argument('content')
        info['contact'] = self.get_argument('contact')
        info['status'] = 1
        info['userid'] = self.admin['userid']
        info['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.db.tb_feedback_profile.insert(info)

        return self.write(json.dumps({"status": "ok", "msg": u'增加反馈成功'}))

class AdminDeleteFeedback(BaseHandler):
    """删除反馈"""

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.tb_feedback_profile.remove({"_id": ObjectId(value[0])})
        return self.write(json.dumps({"status": "ok", "msg": u'删除反馈信息成功'}))

class AdminShopList(BaseHandler):
    """商品列表"""

    # @BaseHandler.admin_authed
    def get(self):
        shop_list = self.db.tb_recharge_package.find().sort("time", pymongo.ASCENDING)
        self.render("backend/shop_list.html", myuser=self.admin, admin_nav=51, shop_list=shop_list)

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.tb_recharge_package.remove({"_id": ObjectId(value[0])})
        return self.write(json.dumps({"status": "ok", "msg": u'删除商品成功'}))


class AdminShopAdd(BaseHandler):
    """商品发布"""

    # @BaseHandler.admin_authed
    def get(self):
        self.render("backend/shop_add.html", myuser=self.admin, admin_nav=7)

    # @BaseHandler.admin_authed
    def post(self):
        info = dict()
        info['gold'] = self.get_argument('gold')
        info['money'] = self.get_argument('money')

        info['buy'] = 0
        info['status'] = 1
        info['userid'] = self.admin.get('userid')
        info['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.db.tb_recharge_package.insert(info)
        return self.write(json.dumps({"status": "ok", "msg": u'增加商品成功'}))

class AdminAddShop(BaseHandler):
    """商品发布"""

    # @BaseHandler.admin_authed
    def get(self):
        self.render("backend/shop_add.html", myuser=self.admin, admin_nav=7)

    # @BaseHandler.admin_authed
    def post(self):
        info = dict()
        info['gold'] = self.get_argument('gold')
        info['money'] = self.get_argument('money')

        info['buy'] = 0
        info['status'] = 1
        info['userid'] = self.admin.get('userid')
        info['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.db.tb_recharge_package.insert(info)
        return self.write(json.dumps({"status": "ok", "msg": u'增加商品成功'}))

class AdminDeleteShop(BaseHandler):
    """删除商品"""

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        del datas['_xsrf']
        # notice = self.settings['notice']
        for key, value in datas.items():
            # course = self.db.tb_notice_profile.find_one({"_id": ObjectId(value[0])})
            self.db.tb_recharge_package.remove({"_id": ObjectId(value[0])})
            # self.db.tb_banner_profile.remove({"pid": value[0], "type": "information"})
            # notice.send(course['uid'], 16, course['id'], 'deleted', course['name'], '')
        self.write(json.dumps({"status": 'ok'}))

class AdminOrderList(BaseHandler):
    """订单列表"""

    # @BaseHandler.admin_authed
    def get(self):
        pay_list = self.db.transaction_record.find()
        print pay_list
        self.render("backend/order_list.html", myuser=self.admin, admin_nav=52, orders=pay_list)

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.transaction_record.remove({"id": int(value[0])})
        return self.write(json.dumps({"status": "success", "error": "", "msg": u'删除订单成功'}))


class AdminActivityList(BaseHandler):
    """活动列表"""

    # @BaseHandler.admin_authed
    def get(self):
        activity_list = self.db.tb_activity_profile.find().sort("time", pymongo.DESCENDING)

        def add_user(userid):
            return self.db.tb_system_user.find_one({"userid": (userid)})

        print activity_list
        self.render("backend/activity_list.html", myuser=self.admin, admin_nav=31, activities=activity_list,
                    add_user=add_user)

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        print datas
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.tb_activity_profile.remove({"_id": ObjectId(value[0])})
        return self.write(json.dumps({"status": "ok", "msg": u'删除活动成功'}))

    # @BaseHandler.admin_authed
    def put(self):
        handler = self.get_argument("handler", "")
        id = self.get_argument("id", 0)
        if handler == "offline":
            self.db.tb_activity_profile.update({"id": int(id)}, {"$set": {"status": "offline"}})
            return self.write(json.dumps({"status": "success", "error": "", "msg": u'更新活动下线状态成功'}))
        elif handler == "online":
            self.db.tb_activity_profile.update({"id": int(id)}, {"$set": {"status": "online"}})
            return self.write(json.dumps({"status": "success", "error": "", "msg": u'更新活动上线状态成功'}))
        else:
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'更新活动状态失败'}))


class AdminActivityAdd(BaseHandler):
    """活动发布"""

    # @BaseHandler.admin_authed
    def get(self):
        self.render("backend/activity_add.html", myuser=self.admin, admin_nav=2)

    # @BaseHandler.admin_authed
    def post(self):
        info = self.request.arguments
        for key, value in info.items():
            if key != 'tag':
                info[key] = value[0]
        del info['_xsrf'], info['index_image']
        info = dict(info)
        info['userid'] = self.admin['userid']
        # search = info.copy()
        info['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
        # # id自增1
        # last = self.db.tb_activity_profile.find().sort("id", pymongo.DESCENDING).limit(1)
        # if last.count() > 0:
        #     lastone = dict()
        #     for item in last:
        #         lastone = item
        #     # 防止刷新更改id
        #     recode = self.db.tb_activity_profile.find_one(search)
        #     if not recode:
        #         info['id'] = int(lastone['id']) + 1
        #     else:
        #         info['id'] = int(recode['id'])
        # else:
        #     info['id'] = 1
        # 当标题重名时，更新
        self.db.tb_activity_profile.update({"id": info['id'], "userid": self.admin['userid']}, {"$set": info}, True)
        self.redirect("/admin/activity_list")

class AdminDeleteActivity(BaseHandler):
    """删除商品"""

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        del datas['_xsrf']
        # notice = self.settings['notice']
        for key, value in datas.items():
            # course = self.db.tb_notice_profile.find_one({"_id": ObjectId(value[0])})
            self.db.tb_recharge_package.remove({"_id": ObjectId(value[0])})
            # self.db.tb_banner_profile.remove({"pid": value[0], "type": "information"})
            # notice.send(course['uid'], 16, course['id'], 'deleted', course['name'], '')
        self.write(json.dumps({"status": 'ok'}))

class AdminTaskList(BaseHandler):
    """任务列表"""

    # @BaseHandler.admin_authed
    def get(self):
        t_type = self.get_argument("type", "")
        query = dict()
        if t_type:
            query.update({
                "type": t_type
            })
        print query
        task_list = self.db.tb_task_profile.find(query).sort("time", pymongo.DESCENDING)

        def add_user(userid):
            return self.db.tb_system_user.find_one({"userid": int(userid)})

        nav = {"everyday": 41, "challenge": 42, "continue": 43}


        print task_list
        self.render("backend/task_list.html", myuser=self.admin, admin_nav=nav.get(t_type,"everyday"), tasks=task_list)

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        print datas
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.tb_task_profile.remove({"id": int(value[0])})
        return self.write(json.dumps({"status": "success", "error": "", "msg": u'删除活动成功'}))

    # @BaseHandler.admin_authed
    def put(self):
        handler = self.get_argument("handler", "")
        id = self.get_argument("id", 0)
        if handler == "offline":
            self.db.tb_task_profile.update({"id": int(id)}, {"$set": {"status": "offline"}})
            return self.write(json.dumps({"status": "success", "error": "", "msg": u'更新活动下线状态成功'}))
        elif handler == "online":
            self.db.tb_task_profile.update({"id": int(id)}, {"$set": {"status": "online"}})
            return self.write(json.dumps({"status": "success", "error": "", "msg": u'更新活动上线状态成功'}))
        else:
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'更新活动状态失败'}))


class AdminTaskAdd(BaseHandler):
    """任务发布"""

    # @BaseHandler.admin_authed
    def get(self):
        self.render("backend/task_add.html", myuser=self.admin, admin_nav=4)

    # @BaseHandler.admin_authed
    def post(self):
        info = self.request.arguments
        for key, value in info.items():
            if key != 'tag':
                info[key] = value[0]
        info = dict(info)
        del info['_xsrf']
        info['userid'] = self.admin['userid']
        search = info.copy()
        info['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
        # id自增1
        last = self.db.tb_task_profile.find().sort("id", pymongo.DESCENDING).limit(1)
        if last.count() > 0:
            lastone = dict()
            for item in last:
                lastone = item
            # 防止刷新更改id
            recode = self.db.tb_task_profile.find_one(search)
            if not recode:
                info['id'] = int(lastone['id']) + 1
            else:
                info['id'] = int(recode['id'])
        else:
            info['id'] = 1
        # 当标题重名时，更新
        self.db.tb_task_profile.update({"id": info['id'], "userid": self.admin['userid']}, {"$set": info}, True)
        self.redirect("/admin/task_list?type="+info['type'])


class AdminDeleteTask(BaseHandler):
    """删除商品"""

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        del datas['_xsrf']
        # notice = self.settings['notice']
        for key, value in datas.items():
            # course = self.db.tb_notice_profile.find_one({"_id": ObjectId(value[0])})
            self.db.tb_task_profile.remove({"_id": ObjectId(value[0])})
            # self.db.tb_banner_profile.remove({"pid": value[0], "type": "information"})
            # notice.send(course['uid'], 16, course['id'], 'deleted', course['name'], '')
        self.write(json.dumps({"status": 'ok'}))

class AdminHistoryList(BaseHandler):
    """股票列表"""

    # @BaseHandler.admin_authed
    def get(self):
        histories = self.db.tb_history_profile.find().sort("time", pymongo.DESCENDING)

        self.render("backend/history_list.html", myuser=self.admin, admin_nav=81, histories=histories)

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        print datas
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.tb_history_profile.remove({"id": int(value[0])})
        return self.write(json.dumps({"status": "success", "error": "", "msg": u'删除股票成功'}))

class AdminDeleteHistory(BaseHandler):
    """删除商品"""

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        del datas['_xsrf']
        # notice = self.settings['notice']
        for key, value in datas.items():
            # course = self.db.tb_notice_profile.find_one({"_id": ObjectId(value[0])})
            self.db.tb_history_profile.remove({"_id": ObjectId(value[0])})
            # self.db.tb_banner_profile.remove({"pid": value[0], "type": "information"})
            # notice.send(course['uid'], 16, course['id'], 'deleted', course['name'], '')
        self.write(json.dumps({"status": 'ok'}))

class AdminStock_list(BaseHandler):
    """股票列表"""

    # @BaseHandler.admin_authed
    def get(self):
        stock_list = self.db.stock.find().sort("time", pymongo.DESCENDING)

        def add_user(userid):
            return self.db.tb_system_user.find_one({"userid": int(userid)})

        self.render("backend/stock_list.html", myuser=self.admin, admin_nav=2, stock_list=stock_list, add_user=add_user)

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        print datas
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.stock.remove({"id": int(value[0])})
        return self.write(json.dumps({"status": "success", "error": "", "msg": u'删除股票成功'}))


class AdminDayline_list(BaseHandler):
    """日K线列表"""

    # @BaseHandler.admin_authed
    def get(self):
        dayline_list = self.db.dayline.find().sort("time", pymongo.DESCENDING)

        def add_user(userid):
            return self.db.tb_system_user.find_one({"userid": int(userid)})

        self.render("backend/dayline_list.html", myuser=self.admin, admin_nav=2, dayline_list=dayline_list, add_user=add_user)

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        print datas
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.dayline.remove({"id": int(value[0])})
        return self.write(json.dumps({"status": "success", "error": "", "msg": u'删除股票成功'}))

class AdminExdividend_list(BaseHandler):
    """股票列表"""

    # @BaseHandler.admin_authed
    def get(self):
        exdividend_list = self.db.exdividend.find().sort("time", pymongo.DESCENDING)

        def add_user(userid):
            return self.db.tb_system_user.find_one({"userid": int(userid)})

        self.render("backend/exdividend_list.html", myuser=self.admin, admin_nav=2, exdividend_list=exdividend_list, add_user=add_user)

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        print datas
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.exdividend.remove({"id": int(value[0])})
        return self.write(json.dumps({"status": "success", "error": "", "msg": u'删除股票成功'}))

class AdminPackage_list(BaseHandler):
    """股票包列表"""

    # @BaseHandler.admin_authed
    def get(self):
        package_list = self.db.package.find().sort("time", pymongo.DESCENDING)

        def add_user(userid):
            return self.db.tb_system_user.find_one({"userid": int(userid)})

        self.render("backend/package_list.html", myuser=self.admin, admin_nav=2, stock_list=stock_list, add_user=add_user)

    # @BaseHandler.admin_authed
    def post(self):
        datas = self.request.arguments
        print datas
        del datas['_xsrf']
        for key, value in datas.items():
            self.db.package.remove({"id": int(value[0])})
        return self.write(json.dumps({"status": "success", "error": "", "msg": u'删除股票成功'}))

class AdminPackage_add(BaseHandler):
    """任务发布"""

    # @BaseHandler.admin_authed
    def get(self):
        self.render("backend/package_add.html", myuser=self.admin, admin_nav=4)

    # @BaseHandler.admin_authed
    def post(self):
        info = self.request.arguments
        for key, value in info.items():
            if key != 'tag':
                info[key] = value[0]
        info = dict(info)
        del info['_xsrf']
        info['userid'] = self.admin['userid']
        search = info.copy()
        info['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
        # id自增1
        last = self.db.package.find().sort("id", pymongo.DESCENDING).limit(1)
        if last.count() > 0:
            lastone = dict()
            for item in last:
                lastone = item

            # 防止刷新更改id
            recode = self.db.package.find_one(search)
            if not recode:
                info['id'] = int(lastone['id']) + 1
            else:
                info['id'] = int(recode['id'])
        else:
            info['id'] = 1

        # 当标题重名时，更新
        self.db.package.update({"id": info['id'], "userid": self.admin['userid']}, {"$set": info}, True)
        self.redirect("/admin/package_list?type="+info['type'])