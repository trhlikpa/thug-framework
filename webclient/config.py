DEBUG = True
ADMINS = ['email@example.com']
SECRET_KEY = 'secret-key'
THREADS_PER_PAGE = 2

CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_TIMEZONE = 'UTC'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYD_MAX_TASKS_PER_CHILD = '1'
CELERY_ROUTES = {
  "worker.thugtask.task.analyze_url": {"queue": "thugtask"},
  "worker.crawltask.task.crawl_urls": {"queue": "crawlertask"}
}

THUG_TIMELIMIT = 600

MONGODB_URL = 'mongodb://db:27017'
MONGODB_DATABASE = 'thug'

GEOIP2_PATH = None

CRAWLER_DOWNLOAD_DELAY = 5
CRAWLER_TIMELIMIT = 3600
