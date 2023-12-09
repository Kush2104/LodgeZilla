import os
import string
import json
import random
import pymongo

mongo_config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'mongo_config.json')


def read_json(src_path):
    with open(src_path, 'r') as json_file:
        json_dict = json.load(json_file)
    return json_dict


def generate_password():
    return ''.join(random.choice(string.printable) for _ in range(10))


def get_mongo_collection(client, collection_name):
    json_content = read_json(mongo_config_file)
    db = client[json_content["database_name"]]
    collection = db[collection_name]
    return collection

def addRandomUserType():
    mongo_config_file_content = read_json(mongo_config_file)
    client = pymongo.MongoClient()
    users_collection = get_mongo_collection(client, mongo_config_file_content["user_collection_name"])

    # Find users without userType field
    users_without_user_type = users_collection.find({"userType": {"$exists": False}})

    # Iterate through each user and update with a random userType
    for user in users_without_user_type:
        random_user_type = random.choice(["host", "tourist"])
        users_collection.update_one({"_id": user["_id"]}, {"$set": {"userType": random_user_type}})

    print("User types randomly allocated for users without userType field.")
    return

addRandomUserType()

    