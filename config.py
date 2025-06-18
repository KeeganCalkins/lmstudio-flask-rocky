import os
from dotenv import load_dotenv

load_dotenv()

# Server Configuration
SERVER_HOST = os.getenv("SERVER_API_HOST", "http://127.0.0.1:1234") 
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "chat_db")
MONGO_COLLECTIONS = {
    "sessions": os.getenv("MONGO_SESSIONS_COLLECTION", "chat_sessions"),
    "messages": os.getenv("MONGO_MESSAGES_COLLECTION", "chat_messages")
}

# Model Configuration
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "google/gemma-3-4b")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "1000"))

# Session Configuration
SESSION_EXPIRY = int(os.getenv("SESSION_EXPIRY", "3600"))  # 1 hour in seconds

# MongoDB Index Configuration
MONGO_INDEXES = {
    "sessions": [
        {"key": "id", "unique": True},
        {"key": "updated_at", "expireAfterSeconds": SESSION_EXPIRY}
    ],
    "messages": [
        {"key": [("session_id", 1), ("created_at", 1)]}
    ]
}
