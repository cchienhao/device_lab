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
        self._devices = {}
        self._selenium_grid_client = SeleniumGridClient()

    def get_all_hubs_url(self):
        session = Session()
        try:
            hubs = session.query(SeleniumGridHub.url).all()
        finally:
            session.close()
        return list(hub.url for hub in hubs)

    def update_devices_in_background(self, period=10):
        def fetch_nodes_by_hub_url(hub_url):
            def on_error(e):
                logger.exception("fail to fetch nodes by url: %s", hub_url)
                return Observable.empty()
            feature = convert_yielded(self._selenium_grid_client.get_devices_by_hub_url_async(hub_url))
            return Observable.from_future(feature) \
                .map(lambda res: (hub_url, json.loads(res.body))) \
                .catch_exception(handler=on_error)  # make sure this observable never emit error

        def update_device(url, res):
            try:
                self._devices.update({url: res['nodes']})
            except:
                logger.exception('fail to update %s', url)
            else:
                logger.info('success to update %s', url)

        Observable.interval(period*1000, scheduler=scheduler) \
            .flat_map(lambda _: Observable.from_(self.get_all_hubs_url())) \
            .retry() \
            .flat_map(fetch_nodes_by_hub_url) \
            .subscribe(lambda url_res: update_device(url_res[0], url_res[1])) \


    def get_devices(self):
        return self._devices


scheduler = IOLoopScheduler()
selenium_grid_service = SeleniumGridService()
# start background job to update devices
selenium_grid_service.update_devices_in_background(1)
