import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


load_dotenv()

MONGO_REMOTE_URI = os.getenv("MONGO_REMOTE_URI", None)
MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME")
MONGO_CONNECTION_NAME = os.getenv("MONGO_CONNECTION_NAME")

if MONGO_REMOTE_URI:
    client = MongoClient(MONGO_REMOTE_URI, server_api=ServerApi('1'))
else:
    client = MongoClient("mongodb://localhost:27017/")

db = client[MONGO_DATABASE_NAME]
collection = db[MONGO_CONNECTION_NAME]

async def store_event_in_db(event):
    try:
        result = collection.insert_one(event)
        print(f"Stored event with id: {result.inserted_id}")
    except Exception as e:
        print(f"Error storing event in MongoDB: {str(e)}")
