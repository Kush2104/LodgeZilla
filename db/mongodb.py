from pymongo import MongoClient
from bson import ObjectId
from app.settings import config

client = MongoClient(config.MONGODB_URI)
db = client[config.MONGODB_DATABASE]

# Implement functions for data access here
