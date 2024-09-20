import os
from pymongo import MongoClient


if not os.getenv("ENV"):
    mongo_uri = "mongodb://localhost:27017/"
else:
    mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)
db = client.github_events
collection = db.events

async def store_event_in_db(event):
    try:
        result = db.events.insert_one(event)
        print(f"Stored event with id: {result.inserted_id}")
    except Exception as e:
        print(f"Error storing event in MongoDB: {str(e)}")
