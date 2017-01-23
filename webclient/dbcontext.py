from pymongo import MongoClient
from webclient import config

db_client = MongoClient(config.MONGODB_URL, connect=False)
db = db_client['thug']
