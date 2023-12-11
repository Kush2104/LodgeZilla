from fastapi import APIRouter, HTTPException, Depends
from .auth import get_current_user
from fastapi.responses import JSONResponse
from typing import List
import os
import pymongo
from ..util.utils import read_json, get_mongo_collection
from bson.json_util import dumps
from ..model.listing import Property

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

@router.get("/list/{user_id}", response_model=List[dict])
async def get_listings(user_id: int):
    listings = list(listing_collection.find({"host": user_id}))
    # Convert ObjectId to string for serialization
    for listing in listings:
        listing["_id"] = str(listing["_id"])

    # Use JSONResponse and bson.json_util.dumps for proper serialization
    return JSONResponse(content=dumps(listings))

@router.post("/add", response_model=Property)
async def create_item(listing: Property, current_user: str = Depends(get_current_user)):
    property_model = listing.dict()
    result = listing_collection.insert_one(property_model)
    return {**listing.dict(), "id": str(result.inserted_id)}

@router.put("/update/{property_id}", response_model=Property)
async def update_property(property_id: int, updated_data: Property,  current_user: str = Depends(get_current_user)):
    existing_data = listing_collection.find_one({"property_id": property_id})
    if existing_data is None:
        raise HTTPException(status_code=404, detail="Property not found")

    merged_data = {**existing_data, **updated_data.dict(exclude_unset=True)}
    listing_collection.update_one({"property_id": property_id}, {"$set": merged_data})
    return merged_data

@router.delete("/delete/{property_id}")
async def delete_property(property_id: int, current_user: str = Depends(get_current_user)):
    existing_data = listing_collection.find_one({"property_id": property_id})
    if existing_data is None:
        raise HTTPException(status_code=404, detail="Property not found")

    # Perform the delete operation
    result = listing_collection.delete_one({"property_id": property_id})

    if result.deleted_count == 1:
        return {"status": "success", "message": "Property deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete property")