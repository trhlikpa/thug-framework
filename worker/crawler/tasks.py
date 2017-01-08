from uuid import uuid4
from worker.celeryapp import celery
from worker.dbcontext import db
from worker.utils.useragents import get_useragent_string


@celery.task()
def crawl(input_data):
    # Lazy load of task dependencies
    from scrapy.crawler import CrawlerProcess
    from scrapy.http.request import Request
    from worker.crawler.urlspider import UrlSpider

    urls = []

    # Scrapy process configuration
    process = CrawlerProcess({
        'USER_AGENT': get_useragent_string(input_data.get('useragent', None)),
        'DOWNLOAD_DELAY': input_data.get('download_delay', 0),
        'DEPTH_LIMIT': input_data.get('depth_limit', 0),
        'RANDOMIZE_DOWNLOAD_DELAY': input_data.get('randomize_download_delay', True),
        'REDIRECT_MAX_TIMES': input_data.get('redirect_max_times', 20),
        'ROBOTSTXT_OBEY': input_data.get('robotstxt_obey', False)
    })

    url = input_data.get('url', None)
    only_internal = input_data.get('only_internal', True)
    allowed_domains = input_data.get('allowed_domains', None)

    if url is None:
        raise AttributeError('URL missing')

    process.crawl(UrlSpider,
                  url=url,
                  only_internal=only_internal,
                  allowed_domains=allowed_domains,
                  callback=lambda link: urls.append(link)
                  )

    process.start(True)

    uuid = uuid4()
    db.jobs.insert_one({'_id': uuid}, {'urls': urls})
