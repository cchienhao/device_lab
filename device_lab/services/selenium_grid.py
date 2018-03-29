import json
import time
import logging
from urllib.parse import urlsplit

from tornado.gen import convert_yielded

from rx import Observable
from rx.concurrency import IOLoopScheduler

from models.db_schema import Session, SeleniumGridHub
from utils.clients.selenium_grid import SeleniumGridClient

logger = logging.getLogger(__name__)


class SimpleLockManager(object):
    def __init__(self, expired=10):
        self._lock = {}  # k: key, v: ts
        self._expired = expired

    @staticmethod
    def get_current_time():
        return time.time()

    def acquire(self, key, refresh=False):
        # non thread safe, using in single thread context
        ts = self.get_current_time()
        if key in self._lock and not refresh:
            raise RuntimeError("cannot lock: {}".format(key))
        self._lock[key] = ts

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
        for key, ts in self._lock.items():
            if current - ts > self._expired:
                logger.warning('found expired key: %s, %s', key, ts)
                expired_keys.append(key)
        for key in expired_keys:
            del self._lock[key]
        total = len(expired_keys)
        if total > 0:
            logger.warning('expired keys are released, total: %s', total)


class SeleniumGridService(object):
    def __init__(self, selenium_grid_client=None, lock_expired=60):
        self._selenium_grid_client = selenium_grid_client or SeleniumGridClient()
        self._capabilities = []
        self._appium_lock = SimpleLockManager(lock_expired)  # key: netloc
        self._udid_lock = SimpleLockManager(lock_expired)  # key: udid

    def get_all_hubs_url(self):
        session = Session()
        try:
            hubs = session.query(SeleniumGridHub.url).all()
        finally:
            session.close()
        return list(hub.url for hub in hubs)

    def get_available_capabilities(self, platform_name,
                                   platform_version, min_platform_version, max_platform_version):
        query = Observable.from_(self._capabilities) \
            .filter(lambda c: platform_name is None or c['capabilities']['platformName'] == platform_name) \
            .filter(lambda c: len(platform_version) == 0 or c['capabilities']['version'] in platform_version) \
            .filter(lambda c: min_platform_version is None or c['capabilities']['version'] >= min_platform_version) \
            .filter(lambda c: max_platform_version is None or c['capabilities']['version'] <= max_platform_version)
        candidates = list(query.to_blocking())
        result, selected_udid, selected_appium = [], set(), set()
        for cap in candidates:
            if cap['capabilities']['UDID'] in selected_udid or cap['appium_url'] in selected_appium:
                continue
            selected_udid.add(cap['capabilities']['UDID'])
            selected_appium.add(cap['appium_url'])
            result.append(cap)
        return result

    def set_capabilities(self, caps):
        self._capabilities = caps

    def update_capabilities(self, *_args):
        Observable.from_(self.get_all_hubs_url(), scheduler=scheduler) \
            .distinct() \
            .flat_map(self._fetch_hub_detail) \
            .to_list() \
            .subscribe(self.set_capabilities)

    def update_capabilities_in_background(self, period=10):
        Observable.interval(period*1000, scheduler=scheduler) \
            .subscribe(self.update_capabilities)

    def _fetch_hub_detail(self, hub_url) -> Observable:
        def unpack_node(node):
            node_url = node['id']
            browsers = node['protocols']['web_driver']['browsers'].values()
            return Observable.from_iterable(browsers) \
                .flat_map(lambda browser: Observable.from_(browser[browser['version']])) \
                .catch_exception(Observable.empty()) \
                .map(lambda cap: cap.update(appium_url=node_url, hub_url=hub_url) or cap)

        def unpack_hub(hub_detail):
            return Observable.from_(hub_detail['nodes']) \
                .flat_map(unpack_node)

        def on_error(_e):
            logger.exception("fail to fetch nodes by url: %s", hub_url)
            return Observable.empty()

        future = convert_yielded(self._selenium_grid_client.get_devices_by_hub_url_async(hub_url))
        return Observable.from_future(future) \
            .map(lambda res: json.loads(res.body)) \
            .flat_map(unpack_hub) \
            .catch_exception(handler=on_error)  # make sure this observable never emit error


def _get_netloc(url):
    (_, netloc, *_) = urlsplit(url)
    return netloc


scheduler = IOLoopScheduler()
selenium_grid_service = SeleniumGridService()
# start background job to update devices
selenium_grid_service.update_capabilities_in_background(5)
