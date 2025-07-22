import os
import uuid
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from flask import g, jsonify
from loginUtils import db

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

def to_oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise ValueError("Invalid ObjectId")

def self_or_admin(target_user_id: str):
    claims = g.user_claims
    me = db.users.find_one({"azureOID": claims["oid"]}, {"_id":1, "isAdmin":1})
    if not me:
        return False, None
    return (me.get("isAdmin") or str(me["_id"]) == target_user_id), me

# testing the function.
# (maybe) TODO: test scripts instead of hardcoding
if __name__ == "__main__":
    test_key = "testkey12345"
    result = validateKey(test_key)
    if result:
        print("API key is valid. User info:", result)
    else:
        print("API key is invalid.")