#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import tornado.ioloop
import tornado.web

from view.mobile import *
from view.ajax import *
from view.mysocket import *
from view.admin import *
from tornado.options import define, options
from tornado.httpserver import HTTPServer
from utils.session import *
from utils.Notice import Notice
from session.session import MongoSessions
from session.auth import MongoAuthentication
# from db.redis_connection import _connect_redis

define("port", default=8001, help="run on the given port", type=int)
define("develop", default=True, help="develop environment", type=bool)

'''
    author:
        zhiwu.yi
    时间:
        2016/1/13
    服务端的架构体系:
        db  : kline (mongodb)
        session : 基于mongodb

'''

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", index),
            (r"/register", kline_register),
            (r"/login", kline_login),
            (r"/logout", kline_logout),
            (r"/play", kline_battle),
            # (r"/ready", game_ready),
            # (r"/quit", room_quit),
            (r"/k_line_Against", k_line_Against),
            (r"/k_line_cgainst", k_line_cgainst),

            (r"/classic", classic_mode),
            (r"/match", match_mode),
            (r"/competitive", competitive_mode),
            (r"/k_line_game", k_line_game),
            (r"/k_line_melee", k_line_melee),
            (r"/k_line_singles", k_line_singles),

            (r"/help", kline_help),
            (r"/message", kline_message),
            (r"/shop", kline_shop),

            (r"/sendcode", sendcode),
            (r"/smscode", smscode),
            (r"/rename", rename),
            (r"/pay_result", pay_result),
            (r"/feedback", feedback),
            (r"/test", test),
            (r"/websocket", ChatSocketHandler),

            (r"/admin/login", AdminLoginHandler),
            (r"/admin/logout", AdminLogoutHandler),
            (r"/admin/home", AdminHomeHandler),

            (r"/admin/users", AdminUserList),
            (r"/admin/user/add", AdminUserAdd),

            (r"/admin/sysusers", AdminSysUsers),
            (r"/admin/sysuser/add", AdminSysUserAdd),
            (r"/admin/sysuser/delete", AdminDeleteSysUser),
            (r"/admin/sysuser/([0-9a-z]{24})", AdminModifySysUser),
            (r"/admin/system/repass", AdminRepassSystem),

            (r"/admin/notices", AdminNoticeList),
            (r"/admin/notice/add", AdminAddNotice),
            (r"/admin/notice/delete", AdminDeleteNotice),
            (r"/admin/notice/([0-9a-z]{24})", AdminModifyNotice),

            (r"/admin/feedbacks", AdminFeedbackList),
            (r"/admin/feedback/add", AdminAddFeedback),
            (r"/admin/feedback/delete", AdminDeleteFeedback),

            (r"/admin/shops", AdminShopList),
            (r"/admin/shop/add", AdminAddShop),
            (r"/admin/shop/delete", AdminDeleteShop),

            (r"/admin/orders", AdminOrderList),

            (r"/admin/activities", AdminActivityList),
            (r"/admin/activity/add", AdminActivityAdd),
            (r"/admin/activity/delete", AdminDeleteActivity),

            (r"/admin/tasks", AdminTaskList),
            (r"/admin/task/add", AdminTaskAdd),
            (r"/admin/task/delete", AdminDeleteTask),

            (r"/admin/histories", AdminHistoryList),
            (r"/admin/history/delete", AdminDeleteHistory),

            (r"/admin/ajax_activity_detail", AdminAjaxActivity_Detail),
            (r"/kindeditor_upload_json", KindeditorUploadImage),
            (r"/file_manager_json", FileManagerJson),

            (r"/ajax/upload_image", UploadImageFile),
            (r"/ajax/loginbonus", loginbonus),
            (r"/ajax/setavatar", Setavatar),
            (r"/ajax/setting", Configure),
            (r"/ajax/pay", ToPay),
            (r"/ajax/userstatus", userstatus),
            (r"/ajax/activities", ActivityList),
            (r"/ajax/kline", KlineSelect),
        ]


        self.sessions = MongoSessions("playkline", "sessions", timeout=30)
        self.frontend_auth = MongoAuthentication("kline", "tb_user_profile", "mobile")
        self.backend_auth = MongoAuthentication("kline", "tb_system_user", "userid")
        self.sessions.clear_all_sessions()
        settings = dict(
            cookie_secret="e446976943b4e8442f099fed1f3fea28462d5832f483a0ed9a3d5d3859f==78d",
            xsrf_cookies=True,
            login_url='/login',
            admin_login_url="/admin/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            upload_path=os.path.join(os.path.dirname(__file__), "static/media"),
            json_path=os.path.join(os.path.dirname(__file__), "json"),
            attachment_path=os.path.join(os.path.dirname(__file__), "attachment"),
            notice=Notice(),
            develop_env="true",
            session_secret="3cdcb1f00803b6e78ab50b466a40b9977db396840c28307f428b25e2277f1bcc",
            session_timeout=1800,
            store_options={
                'redis_host': '127.0.0.1',
                'redis_port': 6380,
                'redis_pass': 'redis123',
            },
            ui_modules = {

            }
        )

        self.settings = settings
        tornado.web.Application.__init__(self, handlers, **settings)
        self.session_manager = SessionManager(settings["session_secret"], settings["store_options"], settings["session_timeout"])


if __name__ == "__main__":
    # tornado.options.parse_command_line()
    # max_buffer_size = 4 * 1024 ** 3  # 4GB
    # app = Application()
    # if not options.develop:
    #     from config import production
    #
    #     app.settings.update(production.config)
    # else:
    #     from config import develop
    #
    #     app.settings.update(develop.config)
    #
    # http_server = HTTPServer(
    #     app,
    #     max_buffer_size=max_buffer_size,
    # )
    # http_server.listen(options.port)
    # print "visit at", "http://127.0.0.1:%s" % options.port
    # tornado.ioloop.IOLoop.instance().start()

    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    print "visit at", "http://127.0.0.1:%s" % options.port
    tornado.ioloop.IOLoop.instance().start()

