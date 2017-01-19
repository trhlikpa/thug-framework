from datetime import datetime
from bson import ObjectId
from worker.celeryapp import celery
from worker.dbcontext import db
from celery import signature


@celery.task(bind=True)
def crawl(self, signatures=None):
    # Lazy load of task dependencies
    from scrapy.crawler import CrawlerProcess
    from worker.crawler.urlspider import UrlSpider
    from worker.utils.useragents import get_useragent_string
    from worker.utils.netutils import get_top_level_domain, check_url
    from worker.utils.exceptions import DatabaseRecordError, UrlFormatError, UrlNotReachedError

    output_data = dict()

    try:
        job = db.jobs.find_one({'_id': ObjectId(self.request.id)})

        if job is None:
            raise DatabaseRecordError('Job not found in database')

        url = job.get('url')

        if url is None:
            raise AttributeError('URL is missing')

        if not check_url(url):
            raise UrlNotReachedError('Specified URL cannot be reached')

        args = job.get('args')

        if args is None:
            raise DatabaseRecordError('Job record has incorrect format')

        user_agent = get_useragent_string(job.get('useragent'))

        if user_agent is None:
            raise ValueError('User agent not found')

        start_time = str(datetime.utcnow().isoformat())

        initial_output_data = {
            '_state': 'STARTED',
            'start_time': start_time,
            'crawler_start_time': start_time
        }

        db.jobs.update_one({'_id': ObjectId(self.request.id)}, {'$set': initial_output_data})

        urls = []

        # Scrapy process configuration
        process = CrawlerProcess({
            'USER_AGENT': user_agent,
            'DEPTH_LIMIT': args.get('depth_limit', 1),
            'DOWNLOAD_DELAY': args.get('download_delay', 0),
            'RANDOMIZE_DOWNLOAD_DELAY': args.get('randomize_download_delay', False),
            'REDIRECT_MAX_TIMES': args.get('redirect_max_times', 30),
            'ROBOTSTXT_OBEY': args.get('robotstxt_obey', False)
        })

        allowed_domains = args.get('allowed_domains')
        only_internal = args.get('only_internal', True)

        if allowed_domains is None or len(allowed_domains) < 1:
            if only_internal:
                domain = get_top_level_domain(url)
                allowed_domains = [domain]
            else:
                allowed_domains = None

        process.crawl(UrlSpider,
                      url=url,
                      allowed_domains=allowed_domains,
                      callback=lambda link: urls.append(link.url)
                      )

        process.start(True)

        end_time = str(datetime.utcnow().isoformat())

        if signatures is None:
            return

        for url in urls:
            for sig in signatures:
                task_id = ObjectId()
                sig = signature(sig)
                sig.apply_async(args=[str(self.request.id), url], task_id=str(task_id))

        output_data = {
            'crawler_end_time': end_time
        }

    except (AttributeError, ValueError, DatabaseRecordError, UrlFormatError, UrlNotReachedError, IOError) as error:
        end_time = str(datetime.utcnow().isoformat())

        output_data = {
            '_state': 'FAILURE',
            '_error': str(error),
            'end_time': end_time,
            'crawler_end_time': end_time
        }

    finally:
        db.jobs.update_one({'_id': ObjectId(self.request.id)}, {'$set': output_data})
