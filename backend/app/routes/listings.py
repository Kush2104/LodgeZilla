from fastapi import APIRouter, HTTPException, Depends
from .auth import get_current_user
from fastapi.responses import JSONResponse
from typing import List
import os
import pymongo
import redis
from ..util.utils import read_json, get_mongo_collection,  push_to_redis
from bson.json_util import dumps
from ..model.listing import Property

router = APIRouter()

uri = "mongodb+srv://maiyaanirudh:F6RPgjEaLMl6CTBs@cluster0.ah1kbxn.mongodb.net/?retryWrites=true&w=majority"
REDIS_KEY = "toWorkers"
redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379
r = redis.StrictRedis(host=redisHost, port=redisPort, db=0)




# MongoDB Connection
mongo_config_file_path = os.path.join(os.path.dirname(__file__), '../config', 'mongo_config.json')
mongo_config_file_content = read_json(mongo_config_file_path)
client = pymongo.MongoClient(uri)
listing_collection = get_mongo_collection(client, mongo_config_file_content["listing_collection_name"])
listing_collection.create_index([("property_id", pymongo.ASCENDING)])

@router.get("/list", response_model=List[dict])
async def get_listings():
    listings = list(listing_collection.find())
    # Convert ObjectId to string for serialization
    for listing in listings:
        listing["_id"] = str(listing["_id"])

    # Use JSONResponse and bson.json_util.dumps for proper serialization
    push_to_redis(listings, r, REDIS_KEY)
    return JSONResponse(content=dumps(listings))

@router.get("/list/{user_id}", response_model=List[dict])
async def get_listings(user_id: int):
    listings = list(listing_collection.find({"host": user_id}))
    # Convert ObjectId to string for serialization
    for listing in listings:
        listing["_id"] = str(listing["_id"])

    # Use JSONResponse and bson.json_util.dumps for proper serialization
    push_to_redis(listings, r, REDIS_KEY)
    return JSONResponse(content=dumps(listings))

@router.post("/add", response_model=Property)
async def create_item(listing: Property, current_user: str = Depends(get_current_user)):
    property_model = listing.dict()
    result = listing_collection.insert_one(property_model)
    push_to_redis("Inserted result id {}".format(result.inserted_id), r, REDIS_KEY)
    return {**listing.dict(), "id": str(result.inserted_id)}

@router.put("/update/{property_id}", response_model=Property)
async def update_property(property_id: int, updated_data: Property,  current_user: str = Depends(get_current_user)):
    existing_data = listing_collection.find_one({"property_id": property_id})
    if existing_data is None:
        raise HTTPException(status_code=404, detail="Property not found")

    merged_data = {**existing_data, **updated_data.dict(exclude_unset=True)}
    listing_collection.update_one({"property_id": property_id}, {"$set": merged_data})
    push_to_redis("Updating property id {} with {}".format(property_id, merged_data), r, REDIS_KEY)
    return merged_data

@router.delete("/delete/{property_id}")
async def delete_property(property_id: int, current_user: str = Depends(get_current_user)):
    existing_data = listing_collection.find_one({"property_id": property_id})
    if existing_data is None:
        raise HTTPException(status_code=404, detail="Property not found")

    # Perform the delete operation
    result = listing_collection.delete_one({"property_id": property_id})

    if result.deleted_count == 1:
        push_to_redis("Deleting property id {} success".format(property_id), r, REDIS_KEY)
        return {"status": "success", "message": "Property deleted successfully"}
    else:
        push_to_redis("Failure in deleting property id {}".format(property_id), r, REDIS_KEY)
        raise HTTPException(status_code=500, detail="Failed to delete property")