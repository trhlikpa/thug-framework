from celery import Celery
import json
import logging
import hashlib
import os
import io
from ThugAPI import *
from Plugins.ThugPlugins import *
from datetime import datetime

with io.open('../config.json', encoding='utf8') as f:
    config = json.load(f)

celery = Celery('thugtasks', broker=config['CELERY_BROKER_URL'])
celery.conf.update(config)

__log__ = logging.getLogger('Thug')
__log__.setLevel(logging.WARN)
__cfgpath__ = '/etc/thug'
__logpath__ = '/opt/thug/logs/'


class ThugScript(ThugAPI):
    def __init__(self, url, useragent):
        self._url = url
        self._useragent = useragent
        ThugAPI.__init__(self, None, __cfgpath__)

    def analyze(self):
        self.set_file_logging()
        self.set_json_logging()

        self.log_init(self._url)
        self.set_useragent(self._useragent)
        self.set_log_quiet()

        url_md5 = hashlib.md5(self._url).hexdigest()
        time = datetime.now().strftime('%Y%m%d%H%M%S%f')
        log_path = os.path.join(__logpath__, url_md5, time)

        self.set_log_dir(log_path)
        ThugPlugins(PRE_ANALYSIS_PLUGINS, self)()
        self.run_remote(self._url)
        ThugPlugins(POST_ANALYSIS_PLUGINS, self)()

        self.log_event()
        return log_path


@celery.task
def check_url(url, useragent):
    thug = ThugScript(url, useragent)
    log_path = thug.analyze()

    json_path = os.path.join(log_path, 'analysis/json/analysis.json')

    with io.open(json_path) as result:
        json_data = json.load(result)
        return json_data
