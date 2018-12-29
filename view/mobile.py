#!/usr/bin/env python
# -*- coding:utf-8 -*-
from BaseHandler import BaseHandler
import json
import time
import logging
import pymongo
from view import *
from view.pay import app_id

class index(BaseHandler):
    """主页"""

    @BaseHandler.authenticated
    def get(self):
        # print self.user, self.admin, "ss"
        user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
        gold_list = self.db.tb_user_profile.find().sort("gold", pymongo.DESCENDING).limit(30)
        winrate_list = self.db.tb_user_profile.find().sort("winrate", pymongo.DESCENDING).limit(30)

        def get_degree(score):
            v= int(score)+1000
            print "my score is ",v
            return v<200 and "LV1" or (v<400 and "LV2" or (v<800 and "LV3" or (v<1300 and "LV4" or (v<2000 and "LV5" or (v<4000 and "LV6" or (v<8000 and "LV7" or (v<13000 and "LV8" or (v<18000 and "LV9" or "LV10"))))))) )

        self.render("frontend/index.html", myuser=user, gold_list=gold_list, winrate_list=winrate_list, get_degree=get_degree)


class kline_register(BaseHandler):
    """注册页"""

    def get(self):
        self.render("frontend/page/register.html", myuser={"userid": ''})

    def post(self):
        nick = self.get_argument('nick', None)
        pwd = self.get_argument('pwd', None)
        mobile = self.get_argument('mobile', None)
        code = self.get_argument('code', None)

        if nick == "":
            return self.write(json.dumps({"status": "error", "msg": u'用户名不能为空'}))
        if pwd == "":
            return self.write(json.dumps({"status": "error", "msg": u'密码不能为空'}))
        if mobile == "":
            return self.write(json.dumps({"status": "error", "msg": u'手机号码不能为空'}))

        user = self.db.tb_user_profile.find_one({'mobile': mobile})
        if user:
            return self.write(json.dumps({"status": "error", "msg": u'该帐号已经注册'}))

        print user

        # if code != self.get_secure_cookie(mobile):
        #     return self.write(json.dumps({"status": "success", "error": "error", "msg": u'短信验证码错误'}))

        last = self.db.tb_user_profile.find().sort("userid", pymongo.DESCENDING).limit(1)
        print last
        userid = id_auto_increment(last, "userid")
        print userid
        user = {
            'userid': userid,
            'nick': nick,  # 用户名
            'avatar': 1,  # 头像
            'gold': 2800,  # 金币数
            'score': 100,  # 积分
            'playtimes': 0,  # 比赛次数
            'wintimes': 0,  # 赢得次数
            'logindays': 0,  # 连续登录天数
            'passwd': pwd,
            'mobile': mobile,
            'regtime': time.strftime("%Y-%m-%d %H:%M:%S"),  # 注册时间
        }
        print user
        # logging.info(('register user %s %s' % (user['mobile'], user['passwd'])))
        rtn = self.application.frontend_auth.register(user)
        if rtn < 0:
            return self.write(json.dumps({"status": "error", "msg": u'注册失败'}))
        # res = self.begin_frontend_session(mobile, pwd)
        # if not res:
        #     return self.write(json.dumps({"status": "success", "msg": u'权限不足', "error": 'error'}))

        print "register success"
        return self.write(json.dumps({"status": "success", "msg": u'注册成功！'}))


class kline_login(BaseHandler):
    """登录页"""

    def get(self):
        nexts = self.request.arguments.get("next")
        referer_url = '/'
        if 'Referer' in self.request.headers:
            referer_url = '/' + '/'.join(self.request.headers['Referer'].split("/")[3:])
            # print referer_url
        if self.user:
            if referer_url != '/register':
                self.redirect(referer_url)
        next = referer_url
        if nexts:
            next = nexts[0]
        self.render("frontend/page/login.html", url=next, error='', myuser={"userid": ''})

    def check_xsrf_cookie(self):
        pass

    def post(self):
        print self.request.arguments
        mobile = self.get_argument('mobile', None)
        pwd = self.get_argument('pwd', None)
        url = self.get_argument('url', None)
        arguments = self.request.arguments
        print arguments
        # info = {}
        # if not mobile  or not pwd or arguments.get('_xsrf', '')[0] == '':
        if not mobile or not pwd:
            return self.render("frontend/page/login.html", url=url, error=u"登录异常", myuser={"userid": ''})

        res = self.begin_frontend_session(mobile, pwd)
        print res
        if not res:
            return self.render("frontend/page/login.html", url=url, error=u"用户名或密码不正确", myuser={"userid": ''})

        print "url is ",url
        if url == '/register':
            self.redirect('/')
        elif url == '':
            self.redirect('/')
        else:
            self.redirect(url)


class k_line_userlogin(BaseHandler):
    """登录接口"""

    def check_xsrf_cookie(self):
        pass

    def post(self):
        mobile = self.get_argument('mobile', None)
        pwd = self.get_argument('pwd', None)
        url = self.get_argument('url', None)
        arguments = self.request.arguments
        print arguments.get('_xsrf', '')[0]
        info = {}
        if mobile == '' or pwd == '' or arguments.get('_xsrf', '')[0] == '':
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'登录异常'}))
        del arguments['_xsrf']

        user = self.db.tb_user_profile.find_one({"mobile": mobile})
        if not user:
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'用户不存在'}))
        print mobile, pwd
        res = self.begin_session(mobile, pwd)
        if not res:
            return self.write(json.dumps({"status": "success", "error": "error", "msg": u'用户名或密码不正确'}))
        else:
            # 登录记录
            info["ip"] = self.request.remote_ip
            info["time"] = time.strftime("%Y-%m-%d %H:%M:%S")

            self.db.logininfo.insert({"userid": self.user['userid'], "mobile": self.user['mobile'], "ip": info['ip'],
                                      "time": info["time"]})

            # 计算连续登录天数
            beginDate = self.tb_user_profile.get('login', {}).get('time', '')
            if beginDate == '':
                logindays = 1
            else:
                day = datediff(beginDate, info["time"])
                if day == 1:
                    logindays = self.user['logindays'] + 1
                    info["reeceive_state"] = 1  # 金币领取状态:1未未领取，0为已领取
                    if logindays > 7:
                        logindays = 1
                elif day == 0:
                    logindays = self.user['logindays']
                    info["reeceive_state"] = self.tb_user_profile.get("login", {}).get("reeceive_state", 1)
                else:
                    logindays = 1
                    info["reeceive_state"] = self.tb_user_profile.get("login", {}).get("reeceive_state", 1)
            if user.get('gametimes', 0) == 0:
                winrate = 0
            else:
                wintimes = float(self.tb_user_profile.get('wintimes', 0))
                gametimefs = float(self.tb_user_profile.get('gametimes', 0))
                winrate = round((wintimes / gametimefs * 100), 1)
            self.db.tb_user_profile.update({"mobile": self.user['mobile']}, {"$set": {"logindays": logindays, "winrate": winrate,
                                                                         "status": "online", "login": info}})
            if url == '/register':
                self.redirect('/')
            elif url == '':
                pass
            else:
                user = self.db.tb_user_profile.find_one({"mobile": mobile})
                del user['_id']
                return self.write(user)


class kline_logout(BaseHandler):
    """退出登录"""

    def get(self):
        self.post()

    def post(self):
        self.end_frontend_session()
        self.redirect('/login')

class kline_battle(BaseHandler):
    """kline比赛"""

    @BaseHandler.authenticated
    def get(self):
        type = self.get_argument("type", '')
        field = self.get_argument("field", '')

        if type == 'single':
            """单人赛"""

            # 1.choose a kline data
            kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
            # print kline

            # 2.calc. the data
            wdaylines = kline.get('daylist')
            sdaylines = wdaylines.split('|')
            # print sdaylines[0]

            # metrics = []
            daylines = []
            maxlines = [float(v) for v in sdaylines[0].split(',')]
            # print "maxlines=",maxlines
            minlines = [float(v) for v in sdaylines[0].split(',')]
            # print "minlines=",minlines
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
            # print maxlines
            # print minlines
            # print daylines

            del kline["daylist"]
            self.render("frontend/page/play_kline.html", myuser=self.user, kline=kline, field=field, maxlines=maxlines, minlines=minlines, daylines=daylines)

        if type == 'fight':
            """对战赛"""

            # 对战赛挑战场

            # 1.有挑战者
            xfrom = self.get_argument("from", None)
            if xfrom:
                print xfrom
                rival = self.db.tb_user_profile.find_one({"userid": xfrom})
                return self.render("frontend/page/challege.html", myuser=self.user, rival=rival, field=field)

            # 2.有玩对战赛者
            # spaceid = "01%02d"%(int(field))
            # print spaceid
            #
            # rooms = self.db.tb_room_profile.find({"spaceid":spaceid,"status":{"$ne":2}}).sort("weight", pymongo.DESCENDING).limit(1)
            # if rooms.count()>1:
            #     room = rooms[0]
            # else:
            #     #TODO:sss
            #     room = {}
            # # pymongo.cursor.Cursor
            # # for x in room:
            # #     print x
            # players = room.get("players",[])
            # print players
            #
            # self.user["state"] = 0
            # players.append(self.user)
            # print players
            # weight = room.get("weight")+10
            # print weight
            # m = self.db.tb_room_profile.update({"_id":room.get("_id")},{"$set":{"players":players,"weight":weight}})
            # print m

            # # 3.机器人对战
            # if not rival:
            #     roberts = self.db.tb_robert_profile.find()
            #     print roberts
            #     rival = random.choice(list(roberts))
            #
            # print "rival=", rival

            return self.render("frontend/page/two_players.html", myuser=self.user, field=field, rival={})

        if type == 'dogfight':
            """混战赛"""

            roberts = self.db.tb_robert_profile.find()
            print roberts
            # rivals = random.sample(list(roberts), 2)
            rivals = random.choice(list(roberts))
            print rivals

            if field == '1':
                # 混战赛初级场
                # user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                # kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/tree_players.html", myuser=self.user, rival=rivals, field=field)

            if field == '2':
                # 混战赛中级场
                # user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                # kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/tree_players.html", myuser=self.user, rival=rivals, field=field)

            if field == '3':
                # # 混战赛高级场
                # user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                # kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/tree_players.html", myuser=self.user, rival=rivals, field=field)

    @BaseHandler.authenticated
    def post(self):
        pass

class game_ready(BaseHandler):
    """比赛准备好"""

    def get(self):
        self.post()

    @BaseHandler.authenticated
    def post(self):
        # self.end_frontend_session()
        # self.redirect('/login')
        userid = self.user.get('userid')
        roomid = self.get_argument("roomid", None)
        if not roomid:
            return self.write(json.dumps({"status": "error", "msg": u'参数错误！'}))

        room = self.db.tb_room_profile.find_one({"roomid":roomid})
        if not room:
            return self.write(json.dumps({"status": "error", "msg": u'房间参数错误！'}))

        print self.request.arguments
        return self.write(json.dumps({"status": "success", "msg": u'游戏开始！'}))

class room_quit(BaseHandler):
    """比赛准备好"""

    def get(self):
        self.post()

    @BaseHandler.authenticated
    def post(self):
        print self.request.arguments

class k_line_Against(BaseHandler):
    """比赛页面"""

    @BaseHandler.authenticated
    def get(self):
        type = self.get_argument("type", '')
        field = self.get_argument("field", '')
        if type == 'singles':
            """单人赛"""
            if field == '1':
                # 单人赛标准场
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/k_line_Against.html", myuser=user, kline=kline)

            if field == '2':
                # 单人赛卖空场
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/k_line_Against.html", myuser=user, kline=kline)

            if field == '3':
                # 单人赛专业场
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/k_line_Against.html", myuser=user, kline=kline)
        if type == 'fight':
            """对战赛"""
            if field == '1':
                # 对战赛初级场
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/k_line_Against.html", myuser=user, kline=kline)

            if field == '2':
                # 对战赛中级场
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/k_line_Against.html", myuser=user, kline=kline)

            if field == '3':
                # 对战赛高级场
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/k_line_Against.html", myuser=user, kline=kline, rival=None)

            if field == '4':
                # 对战赛挑战场
                xfrom = self.get_argument("from", 0)
                # print xfrom
                rival = self.db.tb_user_profile.find_one({"userid": int(xfrom)})
                # print "rival=", rival

                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                print user

                self.render("frontend/page/k_line_Against.html", myuser=user, kline=kline, rival=rival)

        if type == 'dogfight':
            """混战赛"""
            if field == '1':
                # 混战赛初级场
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/k_line_Against.html", myuser=user, kline=kline)

            if field == '2':
                # 混战赛中级场
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/k_line_Against.html", myuser=user, kline=kline)

            if field == '3':
                # 混战赛高级场
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/k_line_Against.html", myuser=user, kline=kline)

class k_line_cgainst(BaseHandler):
    """竞技页面"""

    @BaseHandler.authenticated
    def get(self):
        type = self.get_argument("type", '')
        field = self.get_argument("field", '')
        if type == 'singles':
            """场次"""
            if field == '1':
                # 新人场
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/k_line_cgainst.html", myuser=user, kline=kline)

            if field == '2':
                # 大师场
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/k_line_cgainst.html", myuser=user, kline=kline)

            if field == '3':
                # 精英场
                user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
                kline = self.db.tb_kline_package.find_one({"idx": random.randint(1, 100)})
                self.render("frontend/page/k_line_cgainst.html", myuser=user, kline=kline)



class classic_mode(BaseHandler):
    """经典模式"""

    @BaseHandler.authenticated
    def get(self):
        user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})

        self.render("frontend/page/classic.html", myuser=user)


class match_mode(BaseHandler):
    """比赛模式"""

    @BaseHandler.authenticated
    def get(self):
        user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})

        self.render("frontend/page/match.html", myuser=user)


class competitive_mode(BaseHandler):
    """竞技模式"""

    @BaseHandler.authenticated
    def get(self):
        user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})

        self.render("frontend/page/competitive.html", myuser=user)


class k_line_game(BaseHandler):
    """游戏页"""

    @BaseHandler.authenticated
    def get(self):
        user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})

        self.render("frontend/page/k_line_game.html", myuser=user)


class kline_help(BaseHandler):
    """帮助页面"""

    @BaseHandler.authenticated
    def get(self):
        user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})

        self.render("frontend/page/help.html", myuser=user)


class k_line_melee(BaseHandler):
    """挑战成功"""

    @BaseHandler.authenticated
    def get(self):
        user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})

        self.render("frontend/page/k_line_melee.html", myuser=user)


class kline_message(BaseHandler):
    """个人信息"""

    @BaseHandler.authenticated
    def get(self):
        user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
        notice = self.db.tb_notice_profile.find({"status": 1}).sort("_id", pymongo.DESCENDING).limit(1)
        # login_info = self.db.logininfo.find({"userid": self.user['userid']}).sort("time", pymongo.DESCENDING).limit(10)
        login_info = user.get('login',[])

        self.render("frontend/page/message.html", myuser=user, notice=notice, login_info=login_info)


class kline_shop(BaseHandler):
    """商店页面"""

    @BaseHandler.authenticated
    def get(self):
        user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})
        package = self.db.tb_recharge_package.find()

        # 创建唯一订单号
        while True:
            order_no = "webkline" + random_number(15)
            record = self.db.transaction_record.find_one({"order_no": order_no})
            if not record:
                break
        appid = app_id
        if package.count() == 0:
            package=[{"money":100,"gold":100}]

        self.render("frontend/page/shop.html", myuser=user, package=package, order_no=order_no, appid=appid)


class k_line_singles(BaseHandler):
    """挑战结果"""

    @BaseHandler.authenticated
    def get(self):
        user = self.db.tb_user_profile.find_one({"userid": self.user['userid']})

        self.render("frontend/page/k_line_singles.html", myuser=user)


class test(BaseHandler):
    """测试推送"""

    @BaseHandler.authenticated
    def get(self):
        self.render("soc.html")
