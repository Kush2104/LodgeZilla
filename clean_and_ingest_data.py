import os
import pandas as pd
from bs4 import BeautifulSoup
import pymongo
import emoji
from app.util.utils import read_json, get_mongo_collection, generate_password

mongo_config_file_path = os.path.join(os.path.dirname(__file__), 'config', 'mongo_config.json')
mongo_config_file_content = read_json(mongo_config_file_path)
client = pymongo.MongoClient()
listing_collection = get_mongo_collection(client, mongo_config_file_content["listing_collection_name"])
listing_collection.create_index([("property_id", pymongo.ASCENDING)])
user_collection = get_mongo_collection(client, mongo_config_file_content["user_collection_name"])
user_collection.create_index([("user_id", pymongo.ASCENDING)])


def parse_clean_add_listings_data(src_dir):
    """
    CSV files in src_dir must have a predefined naming format which is listings-{city}.csv
    """
    for file in os.listdir(src_dir):
        if not file.lower().startswith('listings'):
            continue
        file_path = os.path.join(src_dir, file)
        df = pd.read_csv(file_path)
        df = df[df["id"].notna() & df["name"].notna()]
        df["description"].fillna("", inplace=True)
        df["price"].fillna(0, inplace=True)
        df["neighborhood_overview"].fillna("", inplace=True)
        df["neighbourhood_cleansed"].fillna("", inplace=True)

        property_id = df["id"]
        title = df["name"].str.replace("★[0-9.]+", "", regex=True).apply(lambda x: " ".join(" ".join(x.split("·")).split()))
        rating = df["name"].str.extract("★([0-9.]+)").fillna(0).squeeze().apply(lambda x: float(x))
        summary = df["description"].apply(lambda x: " ".join(x.split())) + " " + df["neighborhood_overview"].apply(lambda x: " ".join(x.split()))
        summary = summary.apply(lambda x: BeautifulSoup(x, "html.parser").text)
        price = df["price"].apply(lambda x: float(x.split("$")[1].replace(",", "")) if len(x) > 0 and "$" in x else float(x))
        location = os.path.splitext(file)[0].split("-")[1] + (", " + df["neighbourhood_cleansed"] if not df["neighbourhood_cleansed"].empty else "")
        booking_history = [[]] * len(df)
        clean_df = pd.DataFrame({"property_id": property_id, "title": title, "rating": rating, "summary": summary,
                                 "price": price, "location": location, "booking_history": booking_history})
        data_dict = clean_df.to_dict(orient="records")
        listing_collection.insert_many(data_dict)
    return 1


def parse_clean_add_user_data(src_dir):
    """
    CSV files in src_dir must have a predefined naming format which is reviews-{city}.csv
    """

    for file in os.listdir(src_dir):
        user_id_map = {}
        batch_process = {}
        records_= []
        if not file.lower().startswith('reviews'):
            continue
        file_path = os.path.join(src_dir, file)
        df = pd.read_csv(file_path)
        df = df[df["listing_id"].notna() & df["reviewer_id"].notna() ]
        df["comments"].fillna("", inplace=True)

        df_user_id = df["reviewer_id"]
        df_name = df["reviewer_name"]
        df_listing_id = df["listing_id"]
        df_comments = df["comments"]
        df_comments = df_comments.apply(lambda x: BeautifulSoup(x, "html.parser").text)
        for user_id_, name_, listing_id_, comments_ in zip(df_user_id, df_name, df_listing_id, df_comments):
            comments_ = emoji.demojize(comments_.strip())
            if user_id_ not in user_id_map:
                record_ = {"user_id": user_id_, "password": generate_password(), "name": name_, "trips": {str(listing_id_): [comments_]}}
                records_.append(record_)
                user_id_map[user_id_] = 0
            else:
                if user_id_ not in batch_process:
                    batch_process[user_id_] = {}
                trip_ = "trips.{}".format(listing_id_)

                if trip_ not in batch_process[user_id_]:
                    batch_process[user_id_][trip_] = [comments_]
                else:
                    batch_process[user_id_][trip_].append(comments_)

        user_collection.insert_many(records_)
        if len(batch_process) == 0:
            continue
        bulk_write_updates = []
        for user_id_, updates_ in batch_process.items():
            where_clause = {"user_id": user_id_}
            for k, v in updates_.items():
                update_operation = {"$push": {k: {"$each": v}}}
                bulk_write_updates.append(pymongo.UpdateOne(where_clause, update_operation))
        result = user_collection.bulk_write(bulk_write_updates)
    return 1


import time
if __name__ == "__main__":
    a = time.time()
    data_folder = "data"
    parse_clean_add_listings_data(data_folder)
    parse_clean_add_user_data(data_folder)
    client.close()
    b = time.time()
    print('time: {}'.format(abs(a-b)))

