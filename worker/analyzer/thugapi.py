import logging
import os
import ConfigParser
from thug.ThugAPI import ThugAPI
from worker import config


__log__ = logging.getLogger('Thug')
__log__.setLevel(logging.WARN)
__cfgpath__ = '/etc/thug'
__logpath__ = '/etc/thug/logs/'


class Thug(ThugAPI):
    def __init__(self):
        config_parser = ConfigParser.ConfigParser()

        strs = config.MONGODB_URL.split(':')
        host = strs[1].strip('//')
        port = strs[2]

        config_parser.add_section('mongodb')
        config_parser.set('mongodb', 'enable', 'True')
        config_parser.set('mongodb', 'host', host)
        config_parser.set('mongodb', 'port', port)

        config_parser.add_section('hpfeeds')
        config_parser.set('hpfeeds', 'enable', 'False')
        config_parser.set('hpfeeds', 'host', 'hpfeeds.honeycloud.net')
        config_parser.set('hpfeeds', 'port', '10000')
        config_parser.set('hpfeeds', 'ident', 'q6jyo@hp1')
        config_parser.set('hpfeeds', 'secret', 'edymvouqpfe1ivud')

        with open(os.path.join(__cfgpath__, 'logging.conf'), 'wb') as configfile:
            config_parser.write(configfile)

        ThugAPI.__init__(self)

    def analyze_url(self, url, useragent, referer, java, shockwave, adobepdf, proxy, dom_events, no_cache, web_tracking,
                    url_classifiers, html_classifiers, js_classifiers, vb_classifiers, sample_classifiers):

        if useragent:
            self.set_useragent(useragent)
        else:
            raise AttributeError('User agent is missing')

        if java:
            self.set_javaplugin(java)
        else:
            self.disable_javaplugin()

        if shockwave:
            self.set_shockwave_flash(shockwave)
        else:
            self.disable_shockwave_flash()

        if adobepdf:
            self.set_acropdf_pdf(adobepdf)
        else:
            self.disable_acropdf()

        if proxy:
            self.set_proxy(proxy)

        if referer:
            self.set_referer(referer)

        if dom_events:
            self.set_events(dom_events)

        if no_cache:
            self.set_no_cache()

        if web_tracking:
            self.set_web_tracking()

        if url_classifiers:
            for classifier in url_classifiers:
                self.add_urlclassifier(classifier)

        if html_classifiers:
            for classifier in html_classifiers:
                self.add_htmlclassifier(classifier)

        if js_classifiers:
            for classifier in js_classifiers:
                self.add_jsclassifier(classifier)

        if vb_classifiers:
            for classifier in vb_classifiers:
                self.add_vbsclassifier(classifier)

        if sample_classifiers:
            for classifier in sample_classifiers:
                self.add_sampleclassifier(classifier)

        self.log_init(url)

        self.run_remote(url)

        self.log_event()

        mongo =  __log__.ThugLogging.modules['mongodb']
        return str(mongo.get_url(url))
