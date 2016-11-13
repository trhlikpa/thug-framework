from time import sleep
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from webclient import config

db_client = MongoClient(config['MONGODB_URL'], connect=False)
db = db_client[config['MONGODB_DATABASE']]
