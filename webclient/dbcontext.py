from time import sleep
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from webclient import config

db_client = None
db = None

# Connect to database
for _ in range(1, 5):
    try:
        db_client = MongoClient(config['MONGODB_URL'])
        db = db_client[config['MONGODB_DATABASE']]
        break
    except ConnectionFailure:
        print('Unreachable database. Trying to reconnect')
        sleep(4)
