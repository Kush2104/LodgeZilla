from fastapi import APIRouter, Query, Body, Depends
import os
import pymongo
from ..util.utils import read_json, get_mongo_collection, get_current_user
from ..model.user import User


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
        "title": 1,
        "price": 1,
        "location": 1,
        "rating": 1,
        "booking_history": 1
    }
    properties = list(listing_collection.find(query, projection))

    return properties

@router.post("/reserve/{property_id}")
async def reserve_property(
    property_id: str,
    start_date: str = Body(...),
    end_date: str = Body(...),
    current_user: int = Depends(get_current_user),
):
    # Update the booking history of the property
    booking_entry = {"user_id": str(current_user.id), "start_date": start_date, "end_date": end_date}

    listing_collection.update_one(
        {"property_id": property_id},
        {"$push": {"booking_history": booking_entry}},
    )

    # Update the trips field of the user
    user_collection.update_one(
        {"_id": current_user.id},
        {"$push": {"trips": property_id}},
    )

    return {"message": "Reservation successful"}
