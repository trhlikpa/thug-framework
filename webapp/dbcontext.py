from pymongo import MongoClient
from webapp import config
import gridfs

# Connect to DB
db_client = MongoClient(config.MONGODB_URL, connect=False)
db = db_client['thug']
db_fs = db_client['thugfs']
fs = gridfs.GridFS(db_fs)
