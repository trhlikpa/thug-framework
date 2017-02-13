from worker import config
from pymongo import MongoClient

# Connect to DB
db_client = MongoClient(config.MONGODB_URL, connect=False)
db = db_client['thug']
