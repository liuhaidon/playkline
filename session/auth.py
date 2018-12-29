import pymongo

from passlib.hash import pbkdf2_sha512
from db.database import database as mongodb


class Authentication:
    def login(self, username, password):
        return False

    def logout(self, username):
        return

    def register(self, username, password, acls):
        return False

    def get_acls(self, username):
        return []

    def has_acl(self, username, acl):
        return False


class MongoAuthentication(Authentication):
    def __init__(self, database, collection, field):
        # self._conn = pymongo.Connection(**kwargs)
        self._conn = mongodb.conn
        self._coll = self._conn[database][collection]
        self._field = field

    def login(self, user, password):
        print self._field,user
        record = self._coll.find_one({self._field: user})
        print record
        if not record:
            print "user not exist"
            return False
        password_hash = record['passwd']
        print 666,password_hash
        rs = pbkdf2_sha512.verify(password, password_hash)
        print rs, 999
        return rs


    def logout(self, username):
        return

    def register(self, user):
        print "register=", user
        if not user.get('mobile', None) or not user.get('passwd', None):
            return -1

        record = self._coll.find_one({"mobile": user['mobile']})
        print record
        if record:
            return 1

        password_hash = pbkdf2_sha512.encrypt(user['passwd'])
        user['passwd'] = password_hash

        self._coll.insert(user)
        return 0

    def changepwd(self, mobile, newpwd):
        record = self._coll.find_one({"mobile": mobile})
        if record is None:
            return False
        password_hash = pbkdf2_sha512.encrypt(newpwd)
        if record['pwd'] == password_hash:
            return False
        self._coll.update({'mobile': mobile}, {'$set': {'passwd': password_hash}})
        return True

    def changephone(self, mobile, new_phone):
        record = self._coll.find_one({"mobile": mobile})
        if record is None:
            return False
        self._coll.update({'mobile': mobile}, {'$set': {'mobile': new_phone}})
        return True

    def changepaypwd(self, mobile, newpwd):
        record = self._coll.find_one({"mobile": mobile})
        password_hash = pbkdf2_sha512.encrypt(newpwd)
        if record is None:
            return False
        self._coll.update({'mobile': mobile}, {'$set': {'pay_pwd': password_hash}})
        return True

    def get_acls(self, username):
        record = self._coll.find_one({"username": username})
        if record is None:
            return []
        return record['acl']

    def has_acl(self, username, acl):
        acls = self.get_acls(username)
        return acl in acls
