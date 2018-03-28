import json
import logging
from tornado.gen import convert_yielded

from rx import Observable
from rx.concurrency import IOLoopScheduler

from models.db_schema import Session, SeleniumGridHub
from utils.clients.selenium_grid import SeleniumGridClient

logger = logging.getLogger(__name__)


class SeleniumGridService(object):
    def __init__(self, selenium_grid_client=None):
        self._capabilities = []
        self._selenium_grid_client = selenium_grid_client or SeleniumGridClient()

    def get_all_hubs_url(self):
        session = Session()
        try:
            hubs = session.query(SeleniumGridHub.url).all()
        finally:
            session.close()
        return list(hub.url for hub in hubs)

    def get_available_capabilities(self, platform_name, platform_version,
                                   platform_version_gt, platform_version_gte,
                                   platform_version_lt, platform_version_lte):
        query = Observable.from_(self._capabilities) \
            .filter(lambda cap: not cap['busy']) \
            .filter(lambda cap: platform_name is None or cap['capabilities']['platformName'] == platform_name) \
            .filter(lambda cap: platform_version is None or cap['capabilities']['version'] == platform_version) \
            .filter(lambda cap: platform_version_gt is None or cap['capabilities']['version'] > platform_version_gt) \
            .filter(lambda cap: platform_version_gte is None or cap['capabilities']['version'] >= platform_version_gte) \
            .filter(lambda cap: platform_version_lt is None or cap['capabilities']['version'] < platform_version_lt) \
            .filter(lambda cap: platform_version_lte is None or cap['capabilities']['version'] <= platform_version_lte)
        candidates = list(query.to_blocking())
        result, selected_udid, selected_appium = [], set(), set()
        for cap in candidates:
            if cap['capabilities']['UDID'] in selected_udid or cap['appium_url'] in selected_appium:
                continue
            selected_udid.add(cap['capabilities']['UDID'])
            selected_appium.add(cap['appium_url'])
            result.append(cap)
        return result

    def update_capabilities(self, caps):
        self._capabilities = caps

    def update_capabilities_in_background(self, period=10):
        def fetch_nodes_by_hub_url(hub_url):
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

            def on_error(e):
                logger.exception("fail to fetch nodes by url: %s", hub_url)
                return Observable.empty()

            future = convert_yielded(self._selenium_grid_client.get_devices_by_hub_url_async(hub_url))
            return Observable.from_future(future) \
                .map(lambda res: json.loads(res.body)) \
                .flat_map(unpack_hub) \
                .catch_exception(handler=on_error)  # make sure this observable never emit error

        def update_capabilities(*args):
            Observable.from_(self.get_all_hubs_url(), scheduler=scheduler) \
                .distinct() \
                .flat_map(fetch_nodes_by_hub_url) \
                .to_list() \
                .subscribe(self.update_capabilities)

        Observable.interval(period*1000, scheduler=scheduler) \
            .subscribe(update_capabilities)


scheduler = IOLoopScheduler()
selenium_grid_service = SeleniumGridService()
# start background job to update devices
selenium_grid_service.update_capabilities_in_background(5)
