from pymongo import MongoClient
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv
from config import (
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTIONS,
    MONGO_INDEXES
)

load_dotenv()

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Collections
chat_sessions = db[MONGO_COLLECTIONS["sessions"]]
chat_messages = db[MONGO_COLLECTIONS["messages"]]

# Create indexes
for collection_name, indexes in MONGO_INDEXES.items():
    collection = chat_sessions if collection_name == "sessions" else chat_messages
    for index in indexes:
        keys = index.pop('key')
        collection.create_index(keys, **index)

def create_session(system_message: str) -> str:
    """Create a new chat session and return its ID."""
    session_id = str(uuid.uuid4())
    session = {
        "id": session_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "system_message": system_message
    }
    chat_sessions.insert_one(session)
    return session_id

def get_session(session_id: str):
    """Get a chat session by ID."""
    return chat_sessions.find_one({"id": session_id})

def save_message(session_id: str, role: str, content: str):
    """Save a chat message."""
    message = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "created_at": datetime.utcnow()
    }
    chat_messages.insert_one(message)
    
    # Update session's updated_at timestamp
    chat_sessions.update_one(
        {"id": session_id},
        {"$set": {"updated_at": datetime.utcnow()}}
    )

def get_chat_history(session_id: str):
    """Get all messages for a session, ordered by creation time."""
    return list(chat_messages.find(
        {"session_id": session_id},
        sort=[("created_at", 1)]
    )) 