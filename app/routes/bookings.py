from fastapi import APIRouter, Query, Body, Depends
import os
import pymongo
from ..util.utils import read_json, get_mongo_collection
from .auth import get_current_user
from ..model.user import User
from bson import ObjectId, Int64

router = APIRouter()

# MongoDB Connection
mongo_config_file_path = os.path.join(os.path.dirname(__file__), '../config', 'mongo_config.json')
print(mongo_config_file_path)
mongo_config_file_content = read_json(mongo_config_file_path)
client = pymongo.MongoClient()
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
    properties = list(listing_collection.find(query, projection))

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

    return {"message": "Reservation successful", "updated_property": updated_property, "updated_user": updated_user}
