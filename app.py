import pymongo
client = pymongo.MongoClient()
db = client["mydatabase"]
collection = db["mycollection"]
cursor = collection.find({"propertyId":50999396})
for document in cursor:
    print(document)