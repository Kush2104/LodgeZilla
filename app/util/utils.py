import os
import string
import json
import random

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

def get_current_user():
    # Implement this function to get user id
    return

    