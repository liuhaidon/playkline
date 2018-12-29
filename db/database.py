#!/usr/bin/env python
# -*- coding:utf-8 -*-

from pymongo import MongoClient


class database():
    conn = MongoClient('127.0.0.1')
    # conn = Connection('120.25.105.117')
    db = conn['kline']

    @classmethod
    def getDB(cls):
        return cls.db
