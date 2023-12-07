from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List
import os
import pymongo
from ..util.utils import read_json, get_mongo_collection
from bson.json_util import dumps
from ..model.listing import Property
from ..model.user import User
from datetime import datetime


router = APIRouter()

# MongoDB Connection
mongo_config_file_path = os.path.join(os.path.dirname(__file__), '../config', 'mongo_config.json')
print(mongo_config_file_path)
mongo_config_file_content = read_json(mongo_config_file_path)
client = pymongo.MongoClient()
listing_collection = get_mongo_collection(client, mongo_config_file_content["listing_collection_name"])
listing_collection.create_index([("property_id", pymongo.ASCENDING)])

# API to search properties
@router.get("/search")
async def search_properties(
    destination: str = Query(..., title="Destination"),
    from_date: str = Query(..., title="From Date"),
    to_date: str = Query(..., title="To Date")
):
    query = {
        "location": {"$regex": destination, "$options": "i"},
        "$nor": [
            {
                "booking_history": {
                    "$elemMatch": {
                        "start_date": {"$lt": to_date},
                        "end_date": {"$gt": from_date}
                    }
                }
            },
            {
                "booking_history": {"$exists": False}
            }
        ]
    }

    projection = {
        "_id": 0,
        "title": 1,
        "price": 1,
        "location": 1,
        "rating": 1,
        "booking_history": 1
    }
    properties = list(listing_collection.find(query, projection))

    return properties
