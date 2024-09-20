import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


if os.getenv("ENV") == "production":
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri, server_api=ServerApi('1'))
else:
    mongo_uri = "mongodb://localhost:27017/"
    client = MongoClient(mongo_uri)

db = client.github_events
collection = db.events

async def store_event_in_db(event):
    try:
        result = db.events.insert_one(event)
        print(f"Stored event with id: {result.inserted_id}")
    except Exception as e:
        print(f"Error storing event in MongoDB: {str(e)}")
