# /usr/bin/python
# coding: utf-8
import json

import uuid
import hmac

try:
    import ujson
except ImportError:
    import json as ujson
import hashlib
import redis


class SessionData(dict):
    def __init__(self, session_id, hmac_key):
        self.session_id = session_id
        self.hmac_key = hmac_key


# @property
#	def sid(self):
#		return self.session_id
#	@x.setter
#	def sid(self, value):
#		self.session_id = value

class Session(SessionData):
    def __init__(self, session_manager, request_handler):

        self.session_manager = session_manager
        self.request_handler = request_handler

        try:
            current_session = session_manager.get(request_handler)
        except InvalidSessionException:
            current_session = session_manager.get()
        for key, data in current_session.iteritems():
            self[key] = data
        self.session_id = current_session.session_id
        self.hmac_key = current_session.hmac_key

    def save(self):
        print "save=",self
        self.session_manager.set(self.request_handler, self)


class SessionManager(object):
    def __init__(self, secret, store_options, session_timeout):
        self.secret = secret
        self.session_timeout = session_timeout
        try:
            if store_options['redis_pass']:
                self.redis = redis.StrictRedis(host=store_options['redis_host'], port=store_options['redis_port'],
                                               password=store_options['redis_pass'])
            else:
                self.redis = redis.StrictRedis(host=store_options['redis_host'], port=store_options['redis_port'])
        except Exception as e:
            print e

    def _fetch(self, session_id):
        try:
            session_data = raw_data = self.redis.get(session_id)
            if raw_data:
                self.redis.setex(session_id, self.session_timeout, raw_data)
                session_data = ujson.loads(raw_data)
                # session_data = json.loads(raw_data)

            if isinstance(session_data, dict):
                return session_data

            return {}
        except IOError:
            return {}

    def get(self, request_handler=None):
        if (request_handler == None):
            session_id = self._generate_id()
            print "session_id2=", session_id
            hmac_key = self._generate_hmac(session_id)
            return SessionData(session_id, hmac_key)

        session_id = request_handler.get_secure_cookie("session_id")
        hmac_key = request_handler.get_secure_cookie("verification")

        if not session_id:
            session_id = self._generate_id()
            hmac_key = self._generate_hmac(session_id)
            return SessionData(session_id, hmac_key)

        check_hmac = self._generate_hmac(session_id)
        if hmac_key != check_hmac:
            raise InvalidSessionException()

        session = SessionData(session_id, hmac_key)
        session_data = self._fetch(session_id)
        for key, data in session_data.iteritems():
            session[key] = data

        return session

    def set(self, request_handler, session):
        request_handler.set_secure_cookie("session_id", session.session_id)
        request_handler.set_secure_cookie("verification", session.hmac_key)

        print session.items()
        session_data = ujson.dumps(dict(session.items()))

        self.redis.setex(session.session_id, self.session_timeout, session_data)
        print "sessionmgr set=",session.session_id,session_data

    def _generate_id(self):
        return hashlib.sha256(self.secret + str(uuid.uuid4())).hexdigest()

    def _generate_hmac(self, session_id):
        return hmac.new(session_id, self.secret, hashlib.sha256).hexdigest()


class InvalidSessionException(Exception):
    pass
