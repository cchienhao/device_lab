import json
import time
import logging

from tornado.gen import convert_yielded

from rx import Observable
from rx.concurrency import IOLoopScheduler

from itsdangerous import URLSafeSerializer, BadSignature

from models.db_schema import Session, SeleniumGridHub
from utils.clients.selenium_grid import SeleniumGridClient
from utils.clients.appium import AppiumClient
from utils.managers import SimpleLockManager
from services.base import BaseServiceException
from utils.misc import new_random_string, on_exception_return, get_base_url

from config import LOCK_SECRET


logger = logging.getLogger(__name__)


class LockConflictException(BaseServiceException):
    def __init__(self, err_msg):
        super().__init__(self.CONFLICT_CODE, err_msg)


class LockNotFoundException(BaseServiceException):
    def __init__(self, err_msg):
        super().__init__(self.NOT_FOUND_CODE, err_msg)


class SeleniumGridService(object):
    def __init__(self, selenium_grid_client=None, appium_client=None, secret=new_random_string(20)):
        self._selenium_grid_client = selenium_grid_client or SeleniumGridClient()
        self._appium_client = appium_client or AppiumClient()
        # SimpleLockManager works in non-distributed, single thread context
        # for multi thread context, thread lock is needed
        # for distributed context (multi process), redis is a good choice since its commands are run with exclusive way
        self._appium_lock = SimpleLockManager()  # key: netloc
        self._udid_lock = SimpleLockManager()  # key: udid
        self._signed_serializer = URLSafeSerializer(secret)
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
            .filter(lambda c: not self._appium_lock.is_lock(c['appium_url'])) \
            .filter(lambda c: not self._udid_lock.is_lock(c['capabilities']['UDID'])) \
            .filter(lambda c: platform_name is None or c['capabilities']['platformName'] == platform_name) \
            .filter(lambda c: not platform_version or c['capabilities']['version'] in platform_version) \
            .filter(lambda c: min_platform_version is None or c['capabilities']['version'] >= min_platform_version) \
            .filter(lambda c: max_platform_version is None or c['capabilities']['version'] <= max_platform_version)
        candidates = list(query.to_blocking())
        result, selected_udid, selected_appium = [], set(), set()
        for cap in candidates:
            appium_url = cap['appium_url']
            udid = cap['capabilities']['UDID']
            if appium_url in selected_appium or udid in selected_udid:
                continue
            selected_udid.add(udid)
            selected_appium.add(appium_url)
            cap_token = self._signed_serializer.dumps((appium_url, udid), salt='capability')
            result.append({**cap, "capability_token": cap_token})
        return result

    def update_capabilities_from_remote(self):
        Observable.from_(self.get_all_hubs_url()) \
            .distinct() \
            .flat_map(self._fetch_hub_detail_and_unpack_to_caps) \
            .to_list() \
            .subscribe_on(_scheduler) \
            .subscribe(self.set_capabilities)

    def refresh_capabilities_from_remote(self, period):
        expired = period + 2  # expired should be a bit longer than polling period

        def refresh_capability_lock(appium_url__cap):
            appium_url, cap = appium_url__cap
            self._appium_lock.acquire(appium_url, expired=expired, refresh=True)
            logger.info('refresh appium node: %s', appium_url)
            udid = cap['capabilities'].get('UDID')
            if udid is not None:
                logger.info('refresh udid: %s', udid)
                self._udid_lock.acquire(udid, expired=expired, refresh=True)

        Observable.from_(self._capabilities) \
            .map(lambda cap: cap['appium_url']) \
            .distinct() \
            .flat_map(self._fetch_appium_sessions) \
            .subscribe_on(_scheduler) \
            .subscribe(refresh_capability_lock)

    def lock_capability(self, cap_token, timeout):
        try:
            appium_netloc, udid = self._signed_serializer.loads(cap_token, salt='capability')
        except BadSignature:
            msg = "capability does not exists: {}".format(cap_token)
            logger.info(msg)
            raise LockNotFoundException(msg)
        else:
            return self._lock_capability(appium_netloc, udid, timeout)

    def _lock_capability(self, appium_url, udid, timeout):
        try:
            self._appium_lock.acquire(appium_url, expired=timeout)
            self._udid_lock.acquire(udid, expired=timeout)
        except RuntimeError as e:
            msg = "lock conflict: {}, {}, {}".format(appium_url, udid, str(e))
            logger.info(msg)
            raise LockConflictException(msg)
        expired_at = self._get_current_time() + timeout
        return self._signed_serializer.dumps((appium_url, udid, expired_at), salt='lock')

    def release_capability(self, lock_token):
        try:
            appium_netloc, udid, expired_at = self._signed_serializer.loads(lock_token, salt='lock')
            if expired_at < self._get_current_time():
                raise BadSignature("Expired token")
        except BadSignature as e:
            msg = "lock token does not exists: {}, detail: {}".format(lock_token, str(e))
            logger.info(msg)
            raise LockNotFoundException(msg)
        else:
            self._appium_lock.release(appium_netloc)
            self._udid_lock.release(udid)

    def set_capabilities(self, caps):
        self._capabilities = caps

    def update_capabilities_in_background(self, period=10):
        Observable.interval(period * 1000, scheduler=_scheduler) \
            .subscribe_on(_scheduler) \
            .subscribe(lambda _: self.update_capabilities_from_remote())

    def refresh_capabilities_in_background(self, period=5):
        Observable.interval(period * 1000, scheduler=_scheduler) \
            .subscribe_on(_scheduler) \
            .subscribe(lambda _: self.refresh_capabilities_from_remote(period))

    def release_expired_lock_in_background(self, period=1):
        ob = Observable.interval(period * 1000, scheduler=_scheduler)
        ob \
            .subscribe_on(_scheduler) \
            .subscribe(lambda _: self._appium_lock.release_expired_keys())
        ob \
            .subscribe_on(_scheduler) \
            .subscribe(lambda _: self._udid_lock.release_expired_keys())

    def _fetch_hub_detail_and_unpack_to_caps(self, hub_url) -> Observable:
        def on_error(e):
            logger.error("fail to fetch nodes by url: %s, %s", hub_url, str(e))
            return Observable.empty()

        @on_exception_return(on_error)
        def unpack_node(node):
            appium_netloc = self._get_base_url(node['id'])
            hub_netloc = self._get_base_url(hub_url)
            malform_dto = node['protocols']['web_driver']['browsers']['']
            if 'name' in malform_dto:
                del malform_dto['name']
            if 'version' in malform_dto:
                del malform_dto['version']
            cap_lists = malform_dto.values()  # list of cap_lists
            return Observable.from_(cap_lists) \
                .flat_map(lambda cap_list: Observable.from_(cap_list)) \
                .map(lambda cap: {**cap, 'appium_url': appium_netloc, 'hub_url': hub_netloc})

        @on_exception_return(on_error)
        def unpack_hub(hub_detail):
            return Observable.from_(hub_detail['nodes'])

        future = convert_yielded(self._selenium_grid_client.get_devices_by_hub_url_async(hub_url))
        return Observable.from_future(future) \
            .map(lambda res: json.loads(res.body)) \
            .catch_exception(handler=on_error) \
            .flat_map(unpack_hub) \
            .flat_map(unpack_node)

    def _fetch_appium_sessions(self, appium_url) -> Observable:
        def on_error(e):
            logger.error("fail to fetch appium sessions by url: %s, %s", appium_url, str(e))
            return Observable.empty()

        future = convert_yielded(self._appium_client.get_sessions(appium_url))
        return Observable.from_future(future) \
            .map(lambda res: json.loads(res.body)) \
            .catch_exception(handler=on_error) \
            .flat_map(lambda data: Observable.from_(data['value'])) \
            .map(lambda cap: (appium_url, cap))

    @staticmethod
    def _get_base_url(url):
        return get_base_url(url)

    @staticmethod
    def _get_current_time():
        return int(time.time())


_scheduler = IOLoopScheduler()

selenium_grid_service = SeleniumGridService(secret=LOCK_SECRET)
# start background job
selenium_grid_service.update_capabilities_in_background(10)
selenium_grid_service.release_expired_lock_in_background(1)
selenium_grid_service.refresh_capabilities_in_background(5)
