# encoding:utf-8
import json
import logging
import os
import urllib
import urllib2
import time

from db import database

class Robert():

    def __int__(self):
        self.timeout = 60 * 60 * 24

    @property
    def db(self):
        return database.database.getDB()