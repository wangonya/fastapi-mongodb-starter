from pymongo import MongoClient

from app.core.env import ENV

client = MongoClient(ENV.MONGODB_URL)
db = client[ENV.MONGODB_DBNAME]
