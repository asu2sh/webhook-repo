from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client.github_events
collection = db.events

async def store_event_in_db(event):
    try:
        result = db.events.insert_one(event)
        print(f"Stored event with id: {result.inserted_id}")
    except Exception as e:
        print(f"Error storing event in MongoDB: {str(e)}")
