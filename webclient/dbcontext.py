import io
from flask import json
from pymongo import MongoClient

with io.open('../config.json', encoding='utf8') as f:
    config = json.load(f)

db_client = MongoClient(config['MONGODB_URL'])
db = db_client.thug_database
