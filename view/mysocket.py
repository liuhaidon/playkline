#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import uuid

from tornado.web import HTTPError
from db import database
# /*
# *message id:
# *       1:user login;
# *       2:chat message;
# *       3.game command:
# *    +       1:game ready;
# *    +       2.game start;
# *    +       3.game over;
# *    +       4.game quit;
# *    +       5.game exit;
# *    +       6.game restart;
# *       4:challege request;
# *       5:challege response;
# */
def enum(**enums):
    return type('Enum', (), enums)

MESSAGES = enum(USER_LOGIN=1, USER_CHAT=2, GAME_COMMAND=3, CHALLEGE_REQ=4, CHALLEGE_RSP=5)
COMMANDS = enum(GAME_READY=1, GAME_START=2, GAME_OVER=3, GAME_QUIT=4, GAME_EXIT=5, GAME_RESTART=6)

class Message():
    def __init__(self, msgid, xfrom, xto, content):
        self.xfrom = xfrom
        self.xto = xto
        self.msgid = msgid
        self.body = content

    @property
    def msgid(self):
        return self.msgid

    @property
    def xfrom(self):
        return self.xfrom

    @property
    def xto(self):
        return self.xto

    @property
    def body(self):
        return self.body

    def send(self):
        pass

    def recv(self):
        pass

    def handler(self):
        pass

# class CommandHandler():
#     cmdsDict = {}
#
#     def OnEvent(self, cmdid, param, recv):
#         try:
#             func = self.cmdsDict[cmdid]
#             func(param, recv)
#         except:
#             return None
#
#     def AddEvent(self, cmdid, funcName):
#         self.cmdsDict[cmdid] = funcName

class MessageHandler():
    msgsDict = {}

    def OnEvent(self, message):
        try:
            func = self.msgsDict[message.msgid]
            if func:
                return func(message)
            else:
                print("Message id(%s) has no relational function!"%message.msgid)
        except Exception as ex:
            print ex
            return None

    def AddEvent(self, msgid, func):
        self.msgsDict[msgid] = func


# class message():
#     def __init__(self):
#         pass
#
#     def game_ready(self):
#         pass
#
#     def game_over(self):
#         pass
#
#     def game_quit(self):
#         pass
#
#     def game_exit(self):
#         pass
#
#     def game_restart(self):
#         pass
#
#     def game_start(self):
#         pass


class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 256

    userlist = {}
    user_size = 128
    user = None

    roomlist = []
    room_size = 128

    usersockets={}

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        # print "new client opened"
        ChatSocketHandler.waiters.add(self)

    def on_close(self):
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def update_user(cls, user):
        if cls.userlist.has_key(user.get("from")):
            return

        uuser =database.database.getDB().tb_user_profile.find_one({"userid":user.get("from")},{"_id":0,"passwd":0,"login":0,"settings":0})
        cls.userlist[user.get("from")] = uuser

        print cls.userlist
        # if user in cls.userlist:
        #     return
        # for i in cls.userlist:
        #     # check nickname
        #     if user["content"] == i["content"]: return

        # cls.userlist.append(user)
        # if len(cls.userlist) > cls.user_size:
        #     cls.userlist = cls.userlist[-cls.user_size:]

    @classmethod
    def update_room(cls, room):
        for i in cls.roomlist:
            if (room["content"] == i["content"]): return

        cls.roomlist.append(room)
        if len(cls.roomlist) > cls.room_size:
            cls.roomlist = cls.roomlist[-cls.room_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %r", message)
        print "message=",message
        parsed = tornado.escape.json_decode(message)
        msg = Message(parsed.get("msgid"), parsed.get("from"), parsed.get("to"), parsed.get("content"))



        if(parsed["msgid"] == 1):
            print 'adduser start ...'
            user = {
                "id": str(uuid.uuid4()),
                "msgid": parsed.get("msgid"),
                "from": parsed.get("from"),
                "to": parsed.get("to"),
                "content": parsed.get("content"),
            }
            # user["html"] = tornado.escape.to_basestring(self.render_string("user.html", user=user))

            ChatSocketHandler.usersockets[parsed["from"]] = self
            ChatSocketHandler.update_user(user)
            ChatSocketHandler.send_updates(user)
            return

        if(parsed["msgid"] == 2):
            print "message send to..", parsed["to"]
            chat = {
                "id": str(uuid.uuid4()),
                "msgid": parsed.get("msgid"),
                "from": parsed.get("from"),
                "to": parsed.get("to"),
                "content": parsed.get("content"),
            }
            # chat["html"] = tornado.escape.to_basestring(self.render_string("message.html", message=chat))

            ChatSocketHandler.update_cache(chat)
            waiter = ChatSocketHandler.usersockets[parsed["to"]]
            if waiter:
                print "message send to", parsed["to"]
                # print chat
                waiter.write_message(chat)

            # ChatSocketHandler.send_updates(chat)
            return

        if(parsed["msgid"] == 3):
            print 'game command ...'
            msg = {
                "id": str(uuid.uuid4()),
                "msgid": parsed.get("msgid"),
                "from": parsed.get("from"),
                "to": parsed.get("to"),
                "content": parsed.get("content"),
            }
            # user["html"] = tornado.escape.to_basestring(self.render_string("user.html", user=user))

            ChatSocketHandler.usersockets[parsed["from"]] = self
            # ChatSocketHandler.update_user(user)
            # ChatSocketHandler.send_updates(user)
            roomid = msg.get("content").get("roomid", "")
            spaceid = msg.get("content").get("spaceid", "0101")
            commandid = int(msg.get("content").get("cmdid",1))

            if commandid == 1:   #game ready
                if roomid == "":  #未有房间
                    print "no room,find...."
                    #TODO:匹配对手
                    #1.at first,find a waiting room with someone in;
                    dd = [x for x in ChatSocketHandler.roomlist if x.get("status") == 1 and spaceid == x.get("spaceid")]
                    if len(dd)>0: #选择已有的房间
                        print "find a room!"
                        dd.sort(key=lambda r:r.get("weight"))
                        room = dd[0]

                        local = {"userid": parsed.get("from"), "status": 1}
                        players = room.get("players", [])
                        if len(players)>0:
                            print "has a player in the room!"
                            peer = players[0]
                            peer["status"] = 2
                            local["status"] = 2
                            room["status"] = 2
                            players.append(local)

                            #TODO: send game start message to both
                            print "game start!"
                            msg2 = {
                                "msgid": parsed.get("msgid"),
                                "from": -1,
                                "to": parsed.get("from"),
                                "content": {"cmdid":2,"roomid":room.get("roomid"),"rival":ChatSocketHandler.userlist.get(peer.get("userid"))},
                            }

                            print ChatSocketHandler.usersockets
                            print local,peer
                            print msg2
                            localx = ChatSocketHandler.usersockets[local.get("userid")]
                            print localx
                            if localx:
                                try:
                                    localx.write_message(msg2)
                                except Exception as ex:
                                    print ex
                                    print("Error sending message to myself")

                            msg2["to"] = peer.get("userid")
                            msg2["content"]["rival"] = ChatSocketHandler.userlist.get(local.get("userid"))
                            peerx = ChatSocketHandler.usersockets[peer.get("userid")]
                            print peerx
                            if peerx:
                                try:
                                    peerx.write_message(msg2)
                                except Exception as ex:
                                    print ex
                                    print("Error sending message to peer")
                            return
                        else:
                            players.append(local)

                            #TODO: wait for a new player in
                            return

                    else: #创建一个新房间
                        print "create a room!"
                        room = {"status":1,"roomid":str(uuid.uuid4()),"spaceid":spaceid,"weight":50,"players":[{"userid":parsed.get("from"),"status":1}]}
                        ChatSocketHandler.roomlist.append(room)
                        print ChatSocketHandler.roomlist
                        return
                else:
                    #TODO:已有房间
                    print "has a room!"
                    dd = [v for v in ChatSocketHandler.roomlist if v.get("roomid") == roomid ]
                    room = dd[0]

                    local = {"userid": parsed.get("from"), "status": 1}
                    players = room.get("players", [])
                    if len(players) > 0:
                        peer = players[0]
                        peer["status"] = 2
                        local["status"] = 2
                        room["status"] = 2
                        players.append(local)

                        # TODO: send game start message to both
                        print "game start!"
                        msg2 = {
                            "msgid": parsed.get("msgid"),
                            "from": -1,
                            "to": parsed.get("from"),
                            "content": {"cmdid": 2, "roomid": room.get("roomid"),
                                        "rival": ChatSocketHandler.userlist.get(peer.get("userid"))},
                        }

                        print ChatSocketHandler.usersockets
                        print local, peer
                        print msg2
                        localx = ChatSocketHandler.usersockets[local.get("userid")]
                        print localx
                        if localx:
                            try:
                                localx.write_message(msg2)
                            except Exception as ex:
                                print ex
                                print("Error sending message to myself")

                        msg2["to"] = peer.get("userid")
                        msg2["content"]["rival"] = ChatSocketHandler.userlist.get(local.get("userid"))
                        peerx = ChatSocketHandler.usersockets[peer.get("userid")]
                        print peerx
                        if peerx:
                            try:
                                peerx.write_message(msg2)
                            except Exception as ex:
                                print ex
                                print("Error sending message to peer")
                        return
                    else:
                        players.append(local)

                        # TODO: wait for a new player in
                        return

            elif commandid == 2:  #game start
                pass
            elif commandid == 3:  #game over
                pass
            elif commandid == 4:  #game quit
                pass
            elif commandid == 5:  #game exit
                pass
            elif commandid == 6:  #game restart
                pass
            return


        if(parsed["msgid"] == 4):
            print 'challenge start ...'
            room = {
                "id": str(uuid.uuid4()),
                "msgid": parsed.get("msgid"),
                "from": parsed.get("from"),
                "to": parsed.get("to"),
                "content": parsed.get("content"),
            }

            # challenge["html"] = tornado.escape.to_basestring(self.render_string("user.html", user=user))
            ChatSocketHandler.update_room(room)
            waiter = ChatSocketHandler.usersockets[parsed["to"]]
            if waiter:
                print "challenge send to",parsed["to"]
                print room
                waiter.write_message(room)

        if(parsed["msgid"] == 5):
            print 'challenge response ...'
            print parsed
            rsp = {
                "id": str(uuid.uuid4()),
                "from": parsed["from"],
                "to": parsed["to"],
                "msgid": parsed["msgid"],
                # "content": parsed["content"]
            }
            # print parsed

            # challenge["html"] = tornado.escape.to_basestring(self.render_string("user.html", user=user))
            # ChatSocketHandler.update_room(room)

            print parsed["to"]
            waiter = ChatSocketHandler.usersockets[parsed["to"]]
            if waiter:
                waiter.write_message(rsp)