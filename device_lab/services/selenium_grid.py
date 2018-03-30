import json
import logging
from urllib.parse import urlsplit

from tornado.gen import convert_yielded

from rx import Observable
from rx.concurrency import IOLoopScheduler

from models.db_schema import Session, SeleniumGridHub
from utils.clients.selenium_grid import SeleniumGridClient
from utils.managers import SimpleLockManager, SimpleStoreManager
from services.base import BaseServiceException

logger = logging.getLogger(__name__)


class LockConflictException(BaseServiceException):
    def __init__(self, err_msg):
        super().__init__(self.CONFLICT_CODE, err_msg)


class LockNotFoundException(BaseServiceException):
    def __init__(self, err_msg):
        super().__init__(self.NOT_FOUND_CODE, err_msg)


class SeleniumGridService(object):
    def __init__(self, selenium_grid_client=None):
        self._selenium_grid_client = selenium_grid_client or SeleniumGridClient()
        # SimpleLockManager works in non-distributed, single thread context
        # for multi thread context, thread lock is needed
        # for distributed context (multi process), redis is a good choice since its commands are run with exclusive way
        self._appium_lock = SimpleLockManager()  # key: netloc
        self._udid_lock = SimpleLockManager()  # key: udid
        self._lock_store = SimpleStoreManager()
        self._capabilities = []  # TODO: create a manager to handle capabilities

    def get_all_hubs_url(self):
        session = Session()
        try:
            hubs = session.query(SeleniumGridHub.url).all()
        finally:
            session.close()
        return list(hub.url for hub in hubs)

    def get_available_capabilities(self, platform_name,
                                   platform_version=None, min_platform_version=None, max_platform_version=None):
        query = Observable.from_(self._capabilities) \
            .filter(lambda c: not self._appium_lock.is_lock(self._get_netloc(c['appium_url']))) \
            .filter(lambda c: not self._udid_lock.is_lock(c['capabilities']['UDID'])) \
            .filter(lambda c: platform_name is None or c['capabilities']['platformName'] == platform_name) \
            .filter(lambda c: not platform_version or c['capabilities']['version'] in platform_version) \
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

    def update_capabilities(self, *_args):
        Observable.from_(self.get_all_hubs_url(), scheduler=scheduler) \
            .distinct() \
            .flat_map(self._fetch_hub_detail) \
            .to_list() \
            .subscribe(self.set_capabilities)

    def lock_capability(self, appium_url, udid, timeout):
        appium_netloc = self._get_netloc(appium_url)
        try:
            self._appium_lock.acquire(appium_netloc, expired=timeout)
            self._udid_lock.acquire(udid, expired=timeout)
        except RuntimeError as e:
            msg = "lock conflict: {}, {}, {}".format(appium_url, udid, str(e))
            logger.info(msg)
            raise LockConflictException(msg)
        return self._lock_store.create((appium_netloc, udid))

    def release_capability(self, lock_token):
        ret = self._lock_store.pop(lock_token)
        if ret is None:
            msg = "lock token does not exists: {}".format(lock_token)
            logger.info(msg)
            raise LockNotFoundException(msg)
        appium_netloc, udid = ret
        self._appium_lock.release(appium_netloc)
        self._udid_lock.release(udid)

    def set_capabilities(self, caps):
        self._capabilities = caps

    def update_capabilities_in_background(self, period=10):
        Observable.interval(period*1000, scheduler=scheduler) \
            .subscribe(self.update_capabilities)

    def release_expired_lock_in_background(self, period=1):
        ob = Observable.interval(period*1000, scheduler=scheduler)
        ob.subscribe(lambda _: self._appium_lock.release_expired_keys())
        ob.subscribe(lambda _: self._udid_lock.release_expired_keys())

    def _fetch_hub_detail(self, hub_url) -> Observable:
        def unpack_node(node):
            node_url = node['id']
            malform_dto = node['protocols']['web_driver']['browsers']['']
            if 'name' in malform_dto:
                del malform_dto['name']
            if 'version' in malform_dto:
                del malform_dto['version']
            cap_lists = malform_dto.values()  # list of cap_lists
            return Observable.from_(cap_lists) \
                .flat_map(lambda cap_list: Observable.from_(cap_list)) \
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

    @staticmethod
    def _get_netloc(url):
        (_, netloc, *_) = urlsplit(url)
        return netloc


scheduler = IOLoopScheduler()
selenium_grid_service = SeleniumGridService()
# start background job
selenium_grid_service.update_capabilities_in_background(5)
selenium_grid_service.release_expired_lock_in_background(1)
