from worker import config
from celery import Celery
from pymongo import MongoClient

# Start celery and connect to redis
celery = Celery('tasks', broker=config.CELERY_BROKER_URL)
celery.config_from_object(config)

# Connect to DB
db_client = MongoClient(config.MONGODB_URL, connect=False)
db = db_client[config.MONGODB_DATABASE]
