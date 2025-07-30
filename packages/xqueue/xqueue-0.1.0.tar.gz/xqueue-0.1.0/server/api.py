import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path to import xq modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import redis
import uvicorn

from xq.queue import Queue
from xq.message import Message

# Initialize FastAPI app
app = FastAPI(title="XQ Queue Manager")

# Setup Redis connection
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=False)

# Setup templates
templates = Jinja2Templates(directory="server/templates")

# Create static files directory if it doesn't exist
os.makedirs("server/static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="server/static"), name="static")

# Helper function to get all queue names
def get_queue_names():
    keys = redis_client.keys("xq_prefix_*")
    return [key.decode('utf-8').replace("xq_prefix_", "") for key in keys]

# API Routes
@app.get("/api/queues", response_model=List[str])
async def list_queues():
    """List all available queues"""
    return get_queue_names()

@app.get("/api/queues/{queue_name}/messages")
async def list_messages(queue_name: str):
    """List all messages in a specific queue"""
    queue = Queue(redis_client, queue_name)
    queue_key = f"xq_prefix_{queue_name}"
    
    # Get all messages from the queue
    messages_data = redis_client.zrange(queue_key, 0, -1, withscores=True)
    
    messages = []
    for msg_str, timestamp in messages_data:
        try:
            msg = Message.from_json(msg_str)
            messages.append({
                "id": msg.id,
                "body": msg.body if isinstance(msg.body, str) else str(msg.body),
                "timestamp": msg.timestamp,
                "scheduled_time": datetime.fromtimestamp(msg.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                "cron_expression": msg.cron_expression
            })
        except Exception as e:
            messages.append({
                "error": f"Failed to parse message: {str(e)}",
                "raw": str(msg_str)
            })
    
    return messages

from fastapi import Form, Body

@app.post("/api/queues/{queue_name}/messages")
async def add_message(
    queue_name: str, 
    body: str = Form(None),
    cron_expression: Optional[str] = Form(None),
    request: Request = None
):
    """Add a new message to the queue"""
    # If form data is not provided, try to get from request body
    if body is None and request:
        try:
            json_body = await request.json()
            body = json_body.get("body", "")
            if cron_expression is None:
                cron_expression = json_body.get("cron_expression")
        except:
            # If JSON parsing fails, try to get form data
            form_data = await request.form()
            body = form_data.get("body", "")
            if cron_expression is None:
                cron_expression = form_data.get("cron_expression")
    
    if not body:
        raise HTTPException(status_code=400, detail="Message body is required")
        
    queue = Queue(redis_client, queue_name)
    queue.enqueue(body, cron_expression)
    return {"status": "success", "message": "Message added to queue"}

@app.delete("/api/queues/{queue_name}/messages/{message_id}")
async def delete_message(queue_name: str, message_id: str):
    """Delete a message from the queue"""
    queue_key = f"xq_prefix_{queue_name}"
    
    # Get all messages from the queue
    messages_data = redis_client.zrange(queue_key, 0, -1, withscores=True)
    
    for msg_str, timestamp in messages_data:
        try:
            msg = Message.from_json(msg_str)
            if msg.id == message_id:
                redis_client.zrem(queue_key, msg_str)
                return {"status": "success", "message": "Message deleted"}
        except Exception:
            pass
    
    raise HTTPException(status_code=404, detail="Message not found")

@app.post("/api/queues/{queue_name}/poll")
async def poll_queue(queue_name: str):
    """Poll messages from the queue"""
    queue = Queue(redis_client, queue_name)
    messages = queue.poll()
    
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "body": msg.body if isinstance(msg.body, str) else str(msg.body),
            "timestamp": msg.timestamp,
            "cron_expression": msg.cron_expression
        })
    
    return result

# Web UI Routes
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Render the home page"""
    queues = get_queue_names()
    return templates.TemplateResponse("index.html", {"request": request, "queues": queues})

@app.get("/queues/{queue_name}", response_class=HTMLResponse)
async def queue_page(request: Request, queue_name: str):
    """Render the queue detail page"""
    return templates.TemplateResponse("queue.html", {"request": request, "queue_name": queue_name})

@app.post("/queues/{queue_name}/add")
async def add_message_form(
    request: Request, 
    queue_name: str, 
    body: str = Form(...), 
    cron_expression: Optional[str] = Form(None)
):
    """Handle form submission to add a message"""
    queue = Queue(redis_client, queue_name)
    queue.enqueue(body, cron_expression)
    return RedirectResponse(url=f"/queues/{queue_name}", status_code=303)

def main():
    """Entry point for the console script."""
    uvicorn.run("server.api:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)