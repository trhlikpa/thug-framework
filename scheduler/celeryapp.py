from worker import config
from celery import Celery


# Celery config object
class Config:
    def __init__(self):
        pass

    CELERY_ENABLE_UTC = True
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERYD_MAX_TASKS_PER_CHILD = 1
    BROKER_URL = config.BROKER_URL
    CELERY_RESULT_BACKEND = config.BROKER_URL


# Start celery and connect to redis
celery = Celery('tasks', broker=config.BROKER_URL)
celery.config_from_object(Config)
celery.autodiscover_tasks(['worker.crawler'])
