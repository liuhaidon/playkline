import uuid
import datetime
import logging

from db.database import database as mongodb


class MongoSessions:
    def __init__(self, database, collection, timeout=60, ):
        # self._conn = pymongo.Connection(**kwargs)
        self._conn = mongodb.conn
        self._coll = self._conn[database][collection]
        self._timeout = timeout

    def clear_all_sessions(self):
        logging.debug("Clearing all sesssions.")
        self._coll.remove()

    def new_session(self, data={}):
        id = uuid.uuid4()
        logging.debug("New session: '%s'" % id.hex)
        return self._coll.insert({"_id": id, "ts": datetime.datetime.utcnow(), "data": data}, safe=True)

    def get_session(self, id):
        self._orphan_check()
        logging.debug("Getting session '%s'" % id)

        if id is None:
            return None

        if isinstance(id, str):
            id = uuid.UUID(id)

        record = self._coll.find_one({"_id": id})
        if record is None:
            logging.debug("No record found: '%s'" % id.hex)
            return None

        if not self._compare_timestamp(record['ts']):
            logging.debug("Compare timestamp fail: '%s'" % id.hex)
            self.clear_session(id)
            return None

        self._update_timestamp(id)
        logging.debug(record)
        return record

    def clear_session(self, id):
        print "---------->1",id
        self._orphan_check()

        try:

            print "---------->2",type(id)
            if isinstance(id, str):
                print "---------->22w", id
                sid = uuid.UUID(id)
                print "---------->w", sid
            print "---------->",sid
            return self._coll.remove({"_id": sid})
        except Exception as e:
            print e

    def _orphan_check(self):
        diff = datetime.datetime.utcnow() - datetime.timedelta(minutes=self._timeout)
        self._coll.remove({"ts": {"$lte": diff}})

    def _compare_timestamp(self, ts):
        return ts + datetime.timedelta(minutes=self._timeout) > datetime.datetime.utcnow()

    def _update_timestamp(self, id):
        logging.debug("Updating timestamp")
        self._coll.update({"_id": id}, {
            "$set": {
                "ts": datetime.datetime.utcnow()
            }
        })

    def update(self, _id, _key, _value):
        self._coll.update({"_id": _id}, {
            "$set": {
                _key: _value
            }
        })
