import os
import uuid
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

# Mongo connection
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
keys_collection = db["APIkeys"]

# check if api key is valid
def validateKey(api_key) -> dict | None:
    """
    Checks if the API key exists in the database.
    Returns the user document if found, else None.
    """
    # ensure userID is of ObjectId
    if not isinstance(api_key, ObjectId):
        api_key = ObjectId(api_key)
        
    if not api_key:
        return None
    user = keys_collection.find_one({"_id": api_key})
    return user

# testing the function.
# (maybe) TODO: test scripts instead of hardcoding
if __name__ == "__main__":
    test_key = "testkey12345"
    result = validateKey(test_key)
    if result:
        print("API key is valid. User info:", result)
    else:
        print("API key is invalid.")

# PROBABLY REMOVED SESSION KEY IMPLEMENTATION

# dummy session token storage for testing
# _SESSIONS: dict[str, dict] = {}

# gets session token from ChatRequest
# def getSessionToken(token: str | None) -> str | None:
#     """
#     replace with a Mongo query 
#     """
#     if token and token in _SESSIONS:
#         # If token is valid
#         return token
#     else:
#         # If token is invalid
#         return createSessionToken()
#     return None
# # creates and returns session token
# def createSessionToken():
#     new_token = uuid.uuid4().hex
#     _SESSIONS[new_token] = { "history": [] }
#     return new_token

# # stores messages with corresponding roles to session token 
# def addMessageToSession(token: str, role: str, content: str) -> None:
#     """
#     replace with a Mongo query eg.
#         sessions.update_one(
#             {"token": token},
#             {"$push": {"history": {"role": role, "content": content}}}
#         )
#     """
#     sessionHistory = _SESSIONS[token]
    
#     if role == "user":
#         sessionHistory["last_user"] = content
#     else:
#         sessionHistory["last_assistant"] = content
# # retrieves messages with corresponding roles from session token 
# def getSessionHistory(token: str) -> list[dict]:
#     """
#     replace with a Mongo query 
#     """
#     sessionHistory = _SESSIONS.get(token, {})
#     messageHistory = []
    
#     if "last_user" in sessionHistory:
#         messageHistory.append({"role": "user", "content": sessionHistory["last_user"]})
#     if "last_assistant" in sessionHistory:
#         messageHistory.append({"role": "assistant", "content": sessionHistory["last_assistant"]})
#     return messageHistory