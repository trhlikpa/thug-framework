import datetime
from worker.celeryapp import celery
from worker.dbcontext import db
from worker.utils.useragents import get_useragent_string
from worker.utils.exceptions import DatabaseRecordError


@celery.task(bind=True)
def crawl(self):
    try:
        # Lazy load of task dependencies
        from scrapy.crawler import CrawlerProcess
        from scrapy.http.request import Request
        from worker.crawler.urlspider import UrlSpider

        job = db.jobs.find_one({'_id': self.request.id})

        if job is None:
            raise DatabaseRecordError('Job not found in database')

        input_data = job.get('args')

        if input_data is None:
            raise DatabaseRecordError('Job record has incorrect format')

        initial_output_data = {
            '_state': 'STARTED',
            '_substate': 'CRAWLING - STARTED',
            'crawl_start_time': str(datetime.datetime.utcnow().isoformat())
        }

        db.jobs.update_one({'_id': self.request.id}, {'$set': initial_output_data})

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
            raise AttributeError('URL is missing')

        process.crawl(UrlSpider,
                      url=url,
                      only_internal=only_internal,
                      allowed_domains=allowed_domains,
                      callback=lambda link: urls.append(link.url)
                      )

        process.start(True)

        success_output_data = {
            'urls': urls,
            '_substate': 'CRAWLING - SUCCESS',
            'crawl_end_time': str(datetime.datetime.utcnow().isoformat())
        }

        db.jobs.update_one({'_id': self.request.id}, {'$set': success_output_data})

    except BaseException as error:
        failure_output_data = {
            'urls': [],
            '_state': 'FAILURE',
            '_substate': 'CRAWLING - FAILURE',
            '_error': error.message,
            'crawl_end_time': str(datetime.datetime.utcnow().isoformat())
        }

        db.jobs.update_one({'_id': self.request.id}, {'$set': failure_output_data})

