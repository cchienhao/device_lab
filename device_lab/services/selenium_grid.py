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
        self._hubs_detail = {}  # index by hub_url
        self._selenium_grid_client = selenium_grid_client or SeleniumGridClient()

    def get_all_hubs_url(self):
        session = Session()
        try:
            hubs = session.query(SeleniumGridHub.url).all()
        finally:
            session.close()
        return list(hub.url for hub in hubs)

    def get_devices(self, platform_name, platform_version,
                    platform_version_gt, platform_version_gte, platform_version_lt, platform_version_lte):
        def unpack_node(node):
            node_url = node['id']
            browsers = node['protocols']['web_driver']['browsers'].values()
            return Observable.from_iterable(browsers) \
                .flat_map(lambda browser: Observable.from_(browser[browser['version']])) \
                .catch_exception(Observable.empty()) \
                .map(lambda cap: cap.update(appium_url=node_url) or cap)

        def unpack_hub(url_nodes):
            hub_url, appium_nodes = url_nodes
            return Observable.from_(appium_nodes['nodes']) \
                .flat_map(unpack_node) \
                .map(lambda cap: cap.update(hub_url=hub_url) or cap)

        def group_by_cap(acc, cap):
            if acc is False:  # using False here is if acc is None, reduce will take first item as acc
                acc = cap['capabilities']
            node = {k: v for k, v in cap.items() if k != 'capabilities'}
            acc.setdefault('nodes', []).append(node)
            return acc

        query = Observable.from_(self._hubs_detail.items()) \
            .flat_map(unpack_hub) \
            .group_by(lambda cap: cap['capabilities']['UDID']) \
            .flat_map(lambda group: group.reduce(group_by_cap, False))

        def filter_by_query_params(cap):
            cond = True
            if platform_name is not None:
                cond = cond and cap['capabilities']['platformName'] == platform_name
            if platform_version is not None:
                cond = cond and cap['capabilities']['version'] == platform_version
            if platform_version_gt is not None:
                cond = cond and cap['capabilities']['version'] > platform_version_gt
            if platform_version_gte is not None:
                cond = cond and cap['capabilities']['version'] >= platform_version_gte
            if platform_version_lt is not None:
                cond = cond and cap['capabilities']['version'] < platform_version_lt
            if platform_version_lt is not None:
                cond = cond and cap['capabilities']['version'] <= platform_version_lte
            return cond
        query = query.filter(filter_by_query_params)
        return list(query.to_blocking())

    def update_hubs_detail(self, hubs_detail):
        self._hubs_detail = hubs_detail

    def update_hubs_details_in_background(self, period=10):
        def fetch_nodes_by_hub_url(hub_url):
            def on_error(e):
                logger.exception("fail to fetch nodes by url: %s", hub_url)
                return Observable.empty()
            future = convert_yielded(self._selenium_grid_client.get_devices_by_hub_url_async(hub_url))
            return Observable.from_future(future) \
                .map(lambda res: (hub_url, json.loads(res.body))) \
                .catch_exception(handler=on_error)  # make sure this observable never emit error

        def update_hubs_detail(*args):
            Observable.from_(self.get_all_hubs_url(), scheduler=scheduler) \
                .distinct() \
                .flat_map(fetch_nodes_by_hub_url) \
                .to_dict(lambda url_nodes: url_nodes[0], lambda url_nodes: url_nodes[1]) \
                .subscribe(self.update_hubs_detail)

        Observable.interval(period*1000, scheduler=scheduler) \
            .subscribe(update_hubs_detail)


scheduler = IOLoopScheduler()
selenium_grid_service = SeleniumGridService()
# start background job to update devices
selenium_grid_service.update_hubs_details_in_background(5)
