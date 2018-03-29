import time
import uuid
import logging

logger = logging.getLogger(__name__)


class SimpleLockManager(object):
    def __init__(self):
        self._lock = {}  # k: key, v: expired_at

    @staticmethod
    def get_current_time():
        return time.time()

    def acquire(self, key, expired=5, refresh=False):
        # non thread safe, using in single thread context
        ts = self.get_current_time()
        if key in self._lock and not refresh:
            raise RuntimeError("cannot lock: {}".format(key))
        self._lock[key] = ts + expired

    def release(self, key):
        # non thread safe, using in single thread context
        if key in self._lock:
            del self._lock[key]
        else:
            logger.warning('release an un-acquired key: %s', key)

    def is_lock(self, key):
        return key in self._lock

    def release_expired_keys(self):
        current = self.get_current_time()
        expired_keys = []
        for key, expired_at in self._lock.items():
            if current > expired_at:
                logger.warning('found expired key: %s, %s', key, expired_at)
                expired_keys.append(key)
        for key in expired_keys:
            del self._lock[key]
        total = len(expired_keys)
        if total > 0:
            logger.warning('expired keys are released, total: %s', total)


class SimpleStoreManager(object):
    def __init__(self):
        self._store = {}

    def create(self, obj):
        while True:
            token = self._new_token()
            if token in self._store:
                continue
            self._store[token] = obj
            return token

    def pop(self, token):
        return self._store.pop(token, None)

    @staticmethod
    def _new_token():
        return uuid.uuid4().hex
