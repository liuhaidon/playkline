#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import time
import pymongo
import os
import uuid

from BaseHandler import BaseHandler
from utils import SendSMS
from view import *
from tornado.web import HTTPError
from view.pay import *

class smscode(BaseHandler):
    """短信验证码"""

    def get(self):
        mobile_number = self.get_argument("mobile_number")
        code = random.randint(100000, 999999)
        print code
        self.set_secure_cookie(mobile_number, str(code))
        last_request_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
        last_request_day = datetime.datetime.now() - datetime.timedelta(minutes=1440)

        # 查找一分钟内的register 验证码请求记录
        record = self.db.requests_record.find_one({"type": "register", "ip": self.request.remote_ip,
                                                   "time": {"$gte": last_request_time}})
        # 查找今天的register 验证码请求记录
        day_count = self.db.requests_record.find({"type": "register", "ip": self.request.remote_ip,
                                                  "phone": mobile_number, "time": {"$gte": last_request_day}})
        permit = False if record else True
        print permit
        if permit and day_count.count() < 5:
            # tpl_value = "#code#=%s" % (str(code))
            # tpl_module = '1218461'
            # 发送短信验证码
            SendSMS(code, mobile_number)
            # 写入请求记录表
            self.db.requests_record.insert(
                {"time": datetime.datetime.now(), "type": "register", "ip": self.request.remote_ip})
            return self.write(json.dumps({"status": "success", "msg": u'验证码已发送，请注意获收'}))
        elif day_count.count() >= 5:
            return self.write(json.dumps({"status": "success", "msg": u'今天注册机会已用完,敬请明天再进行注册'}))
        else:
            return self.write(json.dumps({"status": "success", "msg": u'请勿频繁获取验证码'}))

class sendcode(BaseHandler):
    """注册验证码"""

    def get(self):
        mobile_number = self.get_argument("mobile_number")
        code = random.randint(100000, 999999)
        print code
        self.set_cookie(mobile_number, str(code))
        last_request_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
        last_request_day = datetime.datetime.now() - datetime.timedelta(minutes=1440)

        # 查找一分钟内的register 验证码请求记录
        record = self.db.requests_record.find_one({"type": "register", "ip": self.request.remote_ip,
                                                   "time": {"$gte": last_request_time}})
        # 查找今天的register 验证码请求记录
        day_count = self.db.requests_record.find({"type": "register", "ip": self.request.remote_ip,
                                                  "phone": mobile_number, "time": {"$gte": last_request_day}})
        permit = False if record else True
        print permit
        if permit and day_count.count() < 5:
            # tpl_value = "#code#=%s" % (str(code))
            # tpl_module = '1218461'
            # 发送短信验证码
            SendSMS(code, mobile_number)
            # 写入请求记录表
            self.db.requests_record.insert(
                {"time": datetime.datetime.now(), "type": "register", "ip": self.request.remote_ip})
            return self.write(json.dumps({"status": "success", "msg": u'验证码已发送，请注意获收'}))
        elif day_count.count() >= 5:
            return self.write(json.dumps({"status": "success", "msg": u'今天注册机会已用完,敬请明天再进行注册'}))
        else:
            return self.write(json.dumps({"status": "success", "msg": u'请勿频繁获取验证码'}))

class rename(BaseHandler):
    """修改昵称"""

    @BaseHandler.authenticated
    def post(self):
        nick = self.get_argument("nick", '')
        if nick == '' or len(nick) > 32:
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'昵称格式错误'}))
        else:
            self.db.tb_user_profile.update({"userid": self.user['userid']}, {"$set": {"nick": nick}})
            return self.write(json.dumps({"status": "success", "error": "", "msg": u'修改昵称成功'}))


class loginbonus(BaseHandler):
    """获取登录奖励"""

    def post(self):
        logindays = int(self.get_argument("logindays", 1))
        user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})

        if logindays != user.get('logindays'):
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'领取奖励错误'}))

        logininfo = user.get("login")
        lastlogin = logininfo[-1]
        if lastlogin.get("bonus_state", 0) == 1:
            lastlogin['bonus_state'] = 0
            gold = self.db.tb_login_bonus.find_one({"loginday": user.get('logindays')})
            self.db.tb_user_profile.update({"userid": self.user['userid']},
                {"$set": {"gold": self.user['gold'] + gold.get('gold'), "login": logininfo}})
            return self.write(json.dumps({"status": "success", "error": "", "msg": u'领取奖励成功',"gold": gold['gold']}))
        else:
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'你已领过今天的登录奖励'}))


class Setavatar(BaseHandler):
    """修改用户头像"""

    @BaseHandler.authenticated
    def post(self):
        print self.request.arguments
        avatar = self.get_argument("avatar")
        if avatar == '':
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'选择头像参数错误'}))
        if 0 < int(avatar) <= 17:
            self.db.tb_user_profile.update({"userid": self.user['userid']}, {"$set": {"avatar": int(avatar)}})
            return self.write(json.dumps({"status": "success", "error": "", "msg": u'修改头像成功'}))
        else:
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'选择头像参数错误'}))


class Configure(BaseHandler):
    """参数设置"""

    @BaseHandler.authenticated
    def post(self):
        info = self.request.arguments
        print info
        for key, value in info.items():
            if (key not in ["ma5", "_xsrf", "ma20", "ma30", "ma60", "ma10"]) or (value[0] not in ["0", "1"]) and key != \
                    "_xsrf":
                return self.write(json.dumps({"status": "success", "error": "error", "msg": u'传入参数错误'}))
            else:
                info[key] = value[0]
        del info['_xsrf']

        self.db.tb_user_profile.update({"userid": self.user['userid']}, {"$set": {"settings": info}})
        return self.write(json.dumps({"status": "success", "error": "", "msg": u'修改参数成功'}))


class ToPay(BaseHandler):
    """金币充值页面弹窗"""

    def check_xsrf_cookie(self):
        token = json.loads(self.request.body)['_xsrf']
        if not token:
            raise HTTPError(403, "'_xsrf' argument missing from POST")
            # TODO 重构_xsrf验证
            # if self.xsrf_token != token:
            #     print self.xsrf_token
            #     raise HTTPError(403, "XSRF cookie does not match POST argument")

    @BaseHandler.authenticated
    def post(self):
        info = self.request.body
        info = json.loads(info)
        del info['_xsrf']
        myuser = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
        last = self.db.transaction_record.find().sort("_id", pymongo.DESCENDING).limit(1)
        money = int(info['amount'])
        goldpurchas = self.db.goldpurchas.find_one({"money": money})
        gold = goldpurchas['gold']

        if gold:
            info['userid'] = myuser['userid']
            info['status'] = "0"
            info['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
            info['id'] = id_auto_increment(last, "id")
            info['ip'] = self.request.remote_ip
            info['subject'] = "web_kline"
            info['body'] = "web_kline金币" + str((float(money)) / 100) + "元充值"
            info['gold'] = gold

            # 返回支付凭据，记录数据
            ch = payment(info['order_no'], info['channel'], info['amount'], info['subject'], info['body'], info['ip'])
            self.db.transaction_record.insert(info)
            self.db.goldpurchas.update({'id': goldpurchas['id']}, {"$set": {"buy": goldpurchas.get("buy", 0) + 1}})

            return self.write(json.dumps(ch))

        else:
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'传入参数错误'}))


class userstatus(BaseHandler):
    """设置用户状态"""

    @BaseHandler.authenticated
    def post(self):
        t = self.get_argument("type", None)
        if t == 'offline':
            try:
                self.db.tb_user_profile.update({"userid": self.user['userid']}, {"$set": {"status": "offline"}})
                return self.write(json.dumps({"status": "success", "msg": u'用户已退出', "error": ''}))
            except:
                return self.write(json.dumps({"status": "success", "msg": u'用户已退出', "error": ''}))
        elif t == 'online':
            try:
                self.db.tb_user_profile.update({"userid": self.user['userid']}, {"$set": {"status": "online"}})
                return self.write(json.dumps({"status": "success", "msg": u'用户已退出', "error": ''}))
            except:
                return self.write(json.dumps({"status": "success", "msg": u'用户已退出', "error": ''}))
        else:
            return self.write(json.dumps({"status": "success", "msg": u'退出方式错误', "error": 'error'}))


class pay_result(BaseHandler):
    """支付结果"""

    def check_xsrf_cookie(self):
        """去除_xsrf认证"""
        return True

    @BaseHandler.authenticated
    def post(self):
        event = self.request.body
        event = json.loads(event)

        # 第三方调度
        if event['type'] == 'charge.succeeded':
            order_no = event['data']['object']['order_no']
            order_id = event['data']['object']['id']
            ch = pingpp.Charge.retrieve(order_id)
            if str(ch['paid']) == 'True' or str(ch['paid']) == 'true':
                order = self.db.transaction_record.find_one({"order_no": order_no})
                if order.get('status', '') == '0':
                    self.db.transaction_record.update({"order_no": order_no}, {"$set": {"status": "1"}})
                    user = self.db.tb_user_profile.find_one({"userid": order['userid']})
                    self.db.tb_user_profile.update({"userid": order['userid']}, {"$set": {"gold": (int(user['gold']) + int(order['gold'])
                                                                                  )}})
                    goldpurchas = self.db.goldpurchas.find_one({'gold': int(order['gold'])})
                    self.db.goldpurchas.update({'gold': int(order['gold'])},
                                               {"$set": {"payed": goldpurchas.get("payed", 0) + 1}})

                    raise HTTPError(200)
                else:
                    return self.write(json.dumps({"msg": 'Order has been prepaid'}))
            else:
                return self.write(json.dumps({"msg": 'Order not paid'}))

        raise HTTPError(500)


class feedback(BaseHandler):
    """反馈我们"""

    @BaseHandler.authenticated
    def post(self):
        info = dict()
        info['content'] = self.get_argument("content", '')
        # info['contact'] = self.get_argument("contact", '')
        info['contact'] = self.user['mobile']
        if info['content'] == '' or info['contact'] == '':
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'内容或联系方式为空'}))

        if len(info['content']) > 120 or len(info['contact']) > 20:
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'内容或者联系方式过长'}))

        feedback = self.db.tb_feedback_profile.find_one({"content":info['content'],"contact":info['contact']})
        if feedback:
            return self.write(json.dumps({"status": "error", "error": "error", "msg": u'切勿重复提交'}))

        info['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
        info['userid'] = self.user['userid']
        info['name'] = self.user['nick']
        self.db.tb_feedback_profile.insert(info)
        return self.write(json.dumps({"status": "success", "msg": u'感谢您的关注，您的反馈我们已经收到'}))


class UploadImageFile(BaseHandler):
    def post(self):
        path = self.get_argument("path")
        input_name = self.get_argument("iname", "")
        upload_path = os.path.join(self.settings['upload_path'], path)
        # 若不存在此目录，则创建之
        if not os.path.isdir(upload_path):
            upload_path = upload_path.replace("/", "\\")
            os.makedirs(upload_path)
        file_metas = self.request.files.get('file', [])
        filename = ''
        try:
            for meta in file_metas:
                filename = meta['filename']
                ext = os.path.splitext(filename)[1]
                # 生成随机文件名
                filename = str(uuid.uuid4())
                filename = '%s%s' % (filename, ext)
                filepath = os.path.join(upload_path, filename)
                with open(filepath, 'wb') as up:
                    up.write(meta['body'])
        except Exception as e:
            print e
            return self.write(json.dumps({"status": 'error', "msg": u"上传失败，请重新上传"}))
        else:
            print json.dumps({"status": 'ok', "msg": "", "base_url": "", "name": filename})
            return self.write(json.dumps({"status": 'ok', "msg": "", "base_url": "", "name": filename}))


class KindeditorUploadImage(BaseHandler):
    def post(self):
        now_date = time.strftime("%Y%m%d", time.localtime())
        upload_path = os.path.join(self.settings['upload_path'], "editor_upload/%s") % now_date
        base_url = "/static/media/editor_upload/%s/" % now_date
        # 若不存在此目录，则创建之
        if not os.path.isdir(upload_path):
            # os.makedirs(upload_path.replace('/', '\\'))
            os.makedirs(upload_path)
        file_metas = self.request.files.get('imgFile', [])
        filename = ''
        try:
            for meta in file_metas:
                filename = meta['filename']
                ext = os.path.splitext(filename)[1]
                # 生成随机文件名
                filename = str(uuid.uuid4())
                filename = '%s%s' % (filename, ext)
                filepath = os.path.join(upload_path, filename)
                filesize = len(meta['body'])
                with open(filepath, 'wb') as up:
                    up.write(meta['body'])
        except Exception as e:
            self.write(json.dumps({"error": 1, "msg": u"上传失败，请重新上传"}))
        else:
            # 上传记录
            self.db.upload_record.insert(
                {"userid": self.admin['userid'], "filename": filename, "size": filesize, "dir_path": base_url,
                 "time": datetime.datetime.now()})
            self.write(json.dumps({"error": 0, "url": base_url + filename}))


class FileManagerJson(BaseHandler):
    def get(self):
        file_list = []
        for f in self.db.upload_record.find({"userid": self.admin['userid']}):
            file_list.append({
                "is_dir": False,
                "has_file": False,
                "filesize": str(f.get('size', "")),
                "dir_path": f.get('dir_path', ""),
                "is_photo": True,
                "filetype": f['filename'][-3:],
                "filename": f['filename'],
                "datetime": str(datetime)
            })
        self.write(json.dumps(
            {"error": 0, "current_dir_path": "", "current_url": "", "total_count": len(file_list),
             "file_list": file_list}))

class AdminAjaxActivity_Detail(BaseHandler):
    """活动详情ajax"""

    @BaseHandler.authenticated
    def post(self):
        id = self.get_argument("id", 0)
        activity = self.db.tb_activity_profile.find_one({"id": int(id)})
        if activity:
            detail = activity.get('detail')
            title = activity.get('title')
            return self.write(json.dumps({"status": "sucess", "error": "", "msg": "", "detail": detail, "title": title
                                          }))
        else:
            return self.write(json.dumps({"status": "sucess", "error": "error", "msg": "活动不存在", "detail": ""}))


class ActivityList(BaseHandler):
    """活动列表ajax"""

    def get(self):
        activity = self.db.tb_activity_profile.find({"status": "online"}).sort("time", pymongo.DESCENDING)

        ac_list = [{"id": i['id'], "title": i['title'], "image": i['image'], "detail":i['detail'],
                    "abstract":i['abstract'], "time": i['time']} for i in activity]

        return self.write(json.dumps({"list": ac_list, "status": "ok", "error": "",  "num": len(ac_list)}))

class KlineSelect(BaseHandler):
    """ajax 选择k线"""

    def post(self):
        # print self.request.arguments
        kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)},{"_id":0})
        # print kline

        # 2.calc. the data
        wdaylines = kline.get('daylist')
        sdaylines = wdaylines.split('|')
        # print sdaylines[0]

        # metrics = []
        daylines = []
        maxlines = [float(v) for v in sdaylines[0].split(',')]
        print "maxlines=",maxlines
        minlines = [float(v) for v in sdaylines[0].split(',')]
        print "minlines=",minlines
        for v in sdaylines:
            if len(v) < 2:
                break

            dayline = v.split(',')
            dayline2 = [float(m) for m in dayline]
            # print dayline
            daylines.append(dayline2)

            for k, u in enumerate(dayline2):
                if u > maxlines[k]:
                    maxlines[k] = u
                elif u < minlines[k]:
                    minlines[k] = u

        del kline["daylist"]

        print daylines
        data={"status":"ok", "kline":kline, "maxlines":maxlines, "minlines":minlines, "daylines":daylines}
        print data
        return self.write(json.dumps(data))