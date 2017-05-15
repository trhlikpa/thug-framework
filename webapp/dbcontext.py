from pymongo import MongoClient
from webapp import config

# Connect to DB
db_client = MongoClient(config.MONGODB_URL, connect=False)
db = db_client['thug']
