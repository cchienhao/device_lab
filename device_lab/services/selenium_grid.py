import json
import logging
from tornado.gen import convert_yielded

from rx import Observable
from rx.concurrency import IOLoopScheduler

from models.db_schema import Session, SeleniumGridHub
from utils.clients.selenium_grid import SeleniumGridClient

logger = logging.getLogger(__name__)


class SeleniumGridService(object):
    def __init__(self):
        self._hubs_detail = {}  # index by hub_url
        self._selenium_grid_client = SeleniumGridClient()

    def get_all_hubs_url(self):
        session = Session()
        try:
            hubs = session.query(SeleniumGridHub.url).all()
        finally:
            session.close()
        return list(hub.url for hub in hubs)

    def get_devices(self, **kwargs):
        def unpack_node(node):
            node_url = node['id']
            browsers = node['protocols']['web_driver']['browsers'].values()
            return Observable.from_iterable(browsers) \
                .flat_map(lambda browser: Observable.from_(browser[browser['version']])) \
                .catch_exception(Observable.empty()) \
                .map(lambda cap: (node_url, cap))

        def unpack_hub(url_nodes):
            hub_url, appium_nodes = url_nodes
            return Observable.from_(appium_nodes['nodes']) \
                .flat_map(unpack_node) \
                .map(lambda node_url_cap: (hub_url, *node_url_cap))

        query = Observable.from_(self._hubs_detail.items()) \
            .flat_map(unpack_hub)

        platform_name = kwargs.get('platform_name', None)  # Android/iOS
        if platform_name is None:
            raise ValueError("platform name is required")

        def filter_platform_name(hub_node_cap):
            hub_url, node_url, cap = hub_node_cap
            return cap['capabilities']['platformName'] == platform_name
        query = query.filter(filter_platform_name)

        platform_version = kwargs.get('platform_version', None)
        platform_version_gt = kwargs.get('platform_version_gt', None)
        platform_version_gte = kwargs.get('platform_version_gte', None)
        platform_version_lt = kwargs.get('platform_version_lt', None)
        platform_version_lte = kwargs.get('platform_version_lte', None)

        def filter_platform_version(hub_node_cap):
            hub_url, node_url, cap = hub_node_cap
            cond = True
            version = cap['capabilities']['version']
            if platform_version is not None:
                cond = cond and version == platform_version
            if platform_version_gt is not None:
                cond = cond and version > platform_version_gt
            if platform_version_gte is not None:
                cond = cond and version >= platform_version_gte
            if platform_version_lt is not None:
                cond = cond and version < platform_version_lt
            if platform_version_lt is not None:
                cond = cond and version <= platform_version_lte
            return cond
        query = query.filter(filter_platform_version)

        query.subscribe(print)
        return self._hubs_detail

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
