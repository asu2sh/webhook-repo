import json
import urllib.parse
from datetime import datetime
from database import collection, store_event_in_db
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/webhook")
async def github_webhook(request: Request):
    try:
        print("Webhook route hit!")
        content_type = request.headers.get("Content-Type")
        event_type = request.headers.get("X-GitHub-Event")
        print(f"Content-Type: {content_type}, Event Type: {event_type}")

        if content_type == "application/x-www-form-urlencoded":
            form_data = await request.form()
            raw_payload = form_data.get("payload", "")
            decoded_payload = urllib.parse.unquote(raw_payload)
            payload_json = json.loads(decoded_payload)
        elif content_type == "application/json":
            payload_json = await request.json()
        else:
            raise HTTPException(status_code=400, detail="Unsupported Content-Type.")

        if event_type == "push":
            await process_push_event(payload_json)
        elif event_type == "pull_request":
            await process_pull_request_event(payload_json)
        else:
            print(f"Unhandled event type: {event_type}")

        return {"message": "Event processed successfully!"}
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing event: {str(e)}")

async def process_push_event(payload):
    try:
        author = payload['pusher']['name']
        to_branch = payload['ref'].split('/')[-1]
        timestamp = payload['head_commit']['timestamp']

        print(f"{author} pushed to {to_branch} on {timestamp}")

        await store_event_in_db({
            "action": "push",
            "author": author,
            "to_branch": to_branch,
            "timestamp": timestamp,
        })

    except KeyError as e:
        print(f"Missing field in push event payload: {e}")

async def process_pull_request_event(payload):
    try:
        author = payload['pull_request']['user']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        timestamp = payload['pull_request']['created_at']
        
        if payload['pull_request']['merged']:
            merge_author = payload['pull_request']['merged_by']['login']
            merge_timestamp = payload['pull_request']['merged_at']
            
            print(f"{merge_author} merged branch {from_branch} to {to_branch} on {merge_timestamp}")
            
            await store_event_in_db({
                "action": "merge",
                "author": merge_author,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": merge_timestamp,
            })
        else:
            print(f"{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}")
            
            await store_event_in_db({
                "action": "pull_request",
                "author": author,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp,
            })

    except KeyError as e:
        print(f"Missing field in pull request event payload: {e}")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("static/index.html", "r") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@app.get("/events")
async def get_events():
    events = collection.find().sort("timestamp", -1).limit(10)
    event_list = []
    
    for event in events:
        event_list.append({
            "author": event["author"],
            "action": event["action"],
            "from_branch": event.get("from_branch", None),
            "to_branch": event["to_branch"],
            "timestamp": datetime.fromisoformat(event["timestamp"])
        })
    
    sorted_events = sorted(event_list, key=lambda x: x['timestamp'], reverse=True)
    return sorted_events
