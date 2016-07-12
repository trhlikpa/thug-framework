from celery import Celery
import json
import logging
import hashlib
import os
import io
from ThugAPI import *
from Plugins.ThugPlugins import *
from datetime import datetime
from pymongo import MongoClient

with io.open('../config.json', encoding='utf8') as f:
    config = json.load(f)

celery = Celery('thugtasks', broker=config['CELERY_BROKER_URL'])
celery.conf.update(config)

db_client = MongoClient(config['MONGODB_URL'])
db = db_client.thug_database

__log__ = logging.getLogger('Thug')
__log__.setLevel(logging.WARN)
__cfgpath__ = '/etc/thug'
__logpath__ = '/opt/thug/logs/'


class ThugScript(ThugAPI):
    def __init__(self, cfg):
        if not cfg or 'url' not in cfg:
            raise ValueError('URL not found')

        self._cfg = cfg
        ThugAPI.__init__(self, None, __cfgpath__)

    def analyze(self):
        self.set_file_logging()
        self.set_json_logging()
        self.set_log_quiet()

        if len(self._cfg.get('useragent', '')) > 0:
            self.set_useragent(self._cfg['useragent'])

        if len(self._cfg.get('java', '')) > 0:
            self.set_javaplugin(self._cfg['java'])
        else:
            self.disable_javaplugin()

        if len(self._cfg.get('shockwave', '')) > 0:
            self.set_shockwave_flash(self._cfg['shockwave'])
        else:
            self.disable_shockwave_flash()

        if len(self._cfg.get('adobepdf', '')) > 0:
            self.set_acropdf_pdf(self._cfg['adobepdf'])
        else:
            self.disable_acropdf()

        if len(self._cfg.get('proxy', '')) > 0:
            self.set_proxy(self._cfg['proxy'])

        self.log_init(self._cfg['url'])

        url_md5 = hashlib.md5(self._cfg['url']).hexdigest()
        time = datetime.now().strftime('%Y%m%d%H%M%S%f')
        log_path = os.path.join(__logpath__, url_md5, time)

        self.set_log_dir(log_path)
        ThugPlugins(PRE_ANALYSIS_PLUGINS, self)()
        self.run_remote(self._cfg['url'])
        ThugPlugins(POST_ANALYSIS_PLUGINS, self)()

        self.log_event()
        return log_path


@celery.task(bind='true')
def analyze_url(self, data):
    uuid = self.request.id

    json_data = {
        '_state': 'STARTED'
    }

    db.tasks.update({'_id': str(uuid)}, json_data)

    thug = ThugScript(data)
    log_path = thug.analyze()
    json_path = os.path.join(log_path, 'analysis/json/analysis.json')

    try:
        with io.open(json_path) as result:
            data = json.load(result)
            json_data['_state'] = 'SUCCESS'
            json_data.update(data)
    except Exception as error:
        json_data['_state'] = 'FAILURE'
    finally:
        db.tasks.update({'_id': str(uuid)}, json_data)
        db_client.close()
