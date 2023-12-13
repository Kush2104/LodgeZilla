from fastapi import APIRouter, Query, Body, Depends
import os
import pymongo
import logging
from ..util.utils import read_json, get_mongo_collection, push_to_redis
from .auth import get_current_user
from ..config import Constants
from kafka import KafkaProducer
import redis



REDIS_KEY = "toWorkers"
redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379
r = redis.StrictRedis(host=redisHost, port=redisPort, db=0)



# producer = KafkaProducer(bootstrap_servers='172.18.0.3:9092')
# producer = KafkaProducer(bootstrap_servers='localhost:29092')
router = APIRouter()



uri = "mongodb+srv://maiyaanirudh:F6RPgjEaLMl6CTBs@cluster0.ah1kbxn.mongodb.net/?retryWrites=true&w=majority"

# MongoDB Connection
mongo_config_file_path = os.path.join(os.path.dirname(__file__), '../config', 'mongo_config.json')
mongo_config_file_content = read_json(mongo_config_file_path)
client = pymongo.MongoClient(uri)
listing_collection = get_mongo_collection(client, mongo_config_file_content["listing_collection_name"])
listing_collection.create_index([("property_id", pymongo.ASCENDING)])
user_collection = get_mongo_collection(client, mongo_config_file_content["user_collection_name"])
user_collection.create_index([("user_id", pymongo.ASCENDING)])

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
        "property_id": 1,
        "title": 1,
        "price": 1,
        "location": 1,
        "rating": 1,
        "summary": 1
    }



    #push_to_topic(query, producer)
    push_to_redis(query, r, REDIS_KEY)
    properties = list(listing_collection.find(query, projection))
    push_to_redis(properties, r, REDIS_KEY)
    #push_to_topic("searching properties successful with result {}".format(properties), producer)
    return properties


@router.post("/reserve/{property_id}")
async def reserve_property(
    property_id: int,
    start_date: str = Body(...),
    end_date: str = Body(...),
    current_user: int = Depends(get_current_user),
):
    # Update the booking history of the property
    booking_entry = {"user_id": int(current_user), "start_date": start_date, "end_date": end_date}
    updated_property = listing_collection.find_one_and_update(
    {"property_id": property_id},
    {"$push": {"booking_history": booking_entry}},
    return_document=pymongo.ReturnDocument.AFTER
)

    # Convert ObjectId to string for _id field
    updated_property['_id'] = str(updated_property['_id'])

    # Update the trips field of the user
    updated_user = user_collection.find_one_and_update(
        {"user_id": int(current_user)},
        {"$set": {f"trips.{property_id}": []}},
        return_document=pymongo.ReturnDocument.AFTER
    )

    # Convert ObjectId to string for _id field
    updated_user['_id'] = str(updated_user['_id'])

    push_to_redis(updated_property, r, REDIS_KEY)
    push_to_redis(updated_user, r, REDIS_KEY)
    return {"message": "Reservation successful", "updated_property": updated_property, "updated_user": updated_user}
