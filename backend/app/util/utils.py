import os
import string
import json
import random
import pymongo
import logging

mongo_config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'mongo_config.json')
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

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


def encode_to_utf8(msg):
    return str(msg.encode("utf8"))


def push_to_redis(msg, r, REDIS_KEY):
    msg = str(msg)
    count = r.lpush(REDIS_KEY, msg)
    return


def read_from_redis(r, REDIS_KEY):
    while True:
        message = r.blpop(REDIS_KEY)
        print(message)
        logging.debug(message)
