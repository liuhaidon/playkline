#!/usr/bin/env python
# -*- coding:utf-8 -*-

from redis import Redis

class LoginState(object):
    @staticmethod
    def signin(token, user_id):
        r = _connect_redis()
        if r:
            user_key = 'user-token:%s' % token
            p = r.pipeline()
            p.set(user_key, user_id)
            p.execute()

    @staticmethod
    def signout(token):
        r = _connect_redis()
        if r:
            user_key = 'user-token:%s' % token
            p = r.pipeline()
            p.delete(user_key)
            p.execute()

    @staticmethod
    def check_login(token):
        r = _connect_redis()
        if r:
            user_key = 'user-token:%s' % token
            user_id = r.get(user_key)
            if user_id:
                return user_id
            else:
                return -1
        else:
            return -1


def _connect_redis():
    """建立Redis连接"""
    # config = {"REDIS": True, "REDIS_HOST": "120.25.105.117", "REDIS_PORT": 6379, "REDIS_DB": 1}
    config = {"REDIS": True, "REDIS_HOST": "127.0.0.1", "REDIS_PORT": 6380, "REDIS_DB": 1}
    return Redis(host=config.get('REDIS_HOST'), port=config.get('REDIS_PORT'),
                 db=config.get('REDIS_DB'))
