from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List
import os
import pymongo
from ..util.utils import read_json, get_mongo_collection
from bson.json_util import dumps



router = APIRouter()

# MongoDB Connection
mongo_config_file_path = os.path.join(os.path.dirname(__file__), '../config', 'mongo_config.json')
print(mongo_config_file_path)
mongo_config_file_content = read_json(mongo_config_file_path)
client = pymongo.MongoClient()
listing_collection = get_mongo_collection(client, mongo_config_file_content["listing_collection_name"])
listing_collection.create_index([("property_id", pymongo.ASCENDING)])

@router.get("/list", response_model=List[dict])
async def get_listings():
    listings = list(listing_collection.find())
    # Convert ObjectId to string for serialization
    for listing in listings:
        listing["_id"] = str(listing["_id"])

    # Use JSONResponse and bson.json_util.dumps for proper serialization
    return JSONResponse(content=dumps(listings))
