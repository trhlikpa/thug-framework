import hashlib
import logging
import os
from datetime import datetime
from Plugins.ThugPlugins import *
from ThugAPI import *

__log__ = logging.getLogger('Thug')
__log__.setLevel(logging.WARN)
__cfgpath__ = '/etc/thug'
__logpath__ = '/opt/thug/logs/'


class Thug(ThugAPI):
    """
    Class represents thug instance
    """
    def __init__(self, cfg):
        """
        Thug ctor
        :param cfg: thug parameters
        """
        if not cfg or 'url' not in cfg:
            raise ValueError('URL not found')

        self._cfg = cfg
        ThugAPI.__init__(self, None, __cfgpath__)

    def analyze(self):
        """
        Method starts thug analyze
        :return: path to log file
        """
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
