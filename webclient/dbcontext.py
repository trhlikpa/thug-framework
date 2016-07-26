import io
from time import sleep
from flask import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

with io.open('../config.json', encoding='utf8') as f:
    config = json.load(f)

db_client = None
db = None

while True:
    try:
        db_client = MongoClient(config['MONGODB_URL'])
        db = db_client.thug_database
        break
    except ConnectionFailure:
        print('Unreachable database. Trying to reconnect')
        sleep(4)
