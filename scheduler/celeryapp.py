from worker import config
from celery import Celery


# Celery config object
class Config:
    def __init__(self):
        pass

    timezone = 'UTC'
    accept_content = ['application/json']
    task_serializer = 'json'
    result_serializer = 'json'
    worker_max_tasks_per_child = 1
    broker_url = config.BROKER_URL
    result_backend = config.BROKER_URL


# Start celery and connect to redis
celery = Celery('tasks', broker=config.BROKER_URL)
celery.config_from_object(Config)
