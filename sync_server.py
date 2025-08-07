#!/usr/bin/env python3
"""
🚀 Local Network Sync Server
FastAPI server for communication between Streamlit and mobile app
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import json
import os

app = FastAPI(title="Gemma3n Multiverse Sync", version="1.0.0")

# Enable CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (simple but effective for local network)
messages_db = []
pending_messages = []

class Message(BaseModel):
    timestamp: str
    type: str
    message: str
    agent: Optional[str] = None
    response: Optional[str] = None
    status: str = "pending"

@app.get("/")
async def root():
    return {"message": "🧠 Gemma3n Multiverse Sync Server", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message_count": len(messages_db)}

@app.post("/messages")
async def create_message(message: Message):
    """Create a new message (from Streamlit or mobile)"""
    message_dict = message.dict()
    message_dict["id"] = len(messages_db) + 1
    
    if message.status == "pending":
        pending_messages.append(message_dict)
    
    messages_db.append(message_dict)
    print(f"📨 New message: {message.message[:50]}...")
    return {"status": "success", "message_id": message_dict["id"]}

@app.get("/messages/pending")
async def get_pending_messages():
    """Get all pending messages (for mobile app polling)"""
    return {"messages": pending_messages}

@app.put("/messages/{message_id}/response")
async def update_message_response(message_id: int, response: str, status: str = "completed"):
    """Update a message with AI response"""
    for msg in messages_db:
        if msg["id"] == message_id:
            msg["response"] = response
            msg["status"] = status
            if status == "completed":
                # Remove from pending
                pending_messages[:] = [m for m in pending_messages if m["id"] != message_id]
            print(f"✅ Updated message {message_id} with response")
            return {"status": "success"}
    
    raise HTTPException(status_code=404, detail="Message not found")

@app.get("/messages")
async def get_all_messages():
    """Get all messages"""
    return {"messages": messages_db}

@app.delete("/messages")
async def clear_messages():
    """Clear all messages (for testing)"""
    global messages_db, pending_messages
    messages_db.clear()
    pending_messages.clear()
    return {"status": "success", "message": "All messages cleared"}

if __name__ == "__main__":
    print("🚀 Starting Gemma3n Multiverse Sync Server...")
    print("📱 Mobile app can connect to: http://192.168.1.40:8000")
    print("💻 Streamlit can connect to: http://192.168.1.40:8000")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    ) 