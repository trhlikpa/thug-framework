from worker.celeryapp import celery
from worker.crawler.tasks import crawl

celery.autodiscover_tasks(['worker.crawler, worker.thug'])


def execute_job(input_data):
    crawl.apply_async(args=[input_data])


def revoke_job(job_id):
    pass
