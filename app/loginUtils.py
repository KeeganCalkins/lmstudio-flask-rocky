import os
import uuid
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from bson import ObjectId
from datetime import datetime

load_dotenv()

# Mongo connection
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# add user to users collection with unique email
def register_user(userJson):
    if userJson.get("isAdmin", False):
        userJson["hasAccess"] = True
    try:
        result = db.users.insert_one(userJson)
        return {"_id": result.inserted_id}
    except DuplicateKeyError as e:
        raise ValueError("A user with that email is already registered") from e

# remove user using email as key
def remove_user(userID):
    # ensure userID is of ObjectId
    if not isinstance(userID, ObjectId):
        userID = ObjectId(userID)
    try:
        user_deleted = db.users.delete_one({ "_id": userID })
        requests_deleted = remove_access_requests_for_user(userID)
        keys_deleted     = remove_api_keys_for_user(userID)
    except PyMongoError as e:
        raise RuntimeError(f"Failed to delete user: {e}") from e
    if user_deleted.deleted_count == 0:
        raise ValueError(f"No user found with _id {userID!r}")
    return {
        "deleted_user":       user_deleted.deleted_count,
        "deleted_requests":   requests_deleted,
        "deleted_api_keys":   keys_deleted
    }
""" 
Helper functions for the remove user function
"""
# delete pending accessRequest for user
def remove_access_requests_for_user(user_id):
    return db.accessRequests.delete_many({"userID": user_id}).deleted_count
# delete api_keys for user
def remove_api_keys_for_user(user_id):
    return db.APIkeys.delete_many({"userID": user_id}).deleted_count

# Toggles isAdmin
def set_admin(userID, make_admin: bool = True):
    if not isinstance(userID, ObjectId):
        userID = ObjectId(userID)

    set_fields = {"isAdmin": make_admin}
    if make_admin:
        set_fields["hasAccess"] = True
    else:
        db.APIkeys.delete_many({"userID": userID}).deleted_count

    res = db.users.update_one({"_id": userID}, {"$set": set_fields})
    if res.matched_count == 0:
        raise ValueError("No user found with that ID")

    return {"updated_count": res.modified_count, "isAdmin": make_admin}

# remove user's access
def revoke_access(userID):
    if not isinstance(userID, ObjectId):
        userID = ObjectId(userID)

    user = db.users.find_one({"_id": userID}, {"hasAccess": 1})
    if not user:
        raise ValueError("No user found with that ID")

    update_res = db.users.update_one({"_id": userID}, {"$set": {"hasAccess": False}})
    keys_deleted = db.APIkeys.delete_many({"userID": userID}).deleted_count
    reqs_deleted = db.accessRequests.delete_many({"userID": userID}).deleted_count

    return {
        "updated_count": update_res.modified_count,
        "deleted_api_keys": keys_deleted,
        "deleted_requests": reqs_deleted
    }

# add accessRequest with users' _id as userID and email
def request_access(userID):
    # ensure userID is of ObjectId
    if not isinstance(userID, ObjectId):
        userID = ObjectId(userID)
        
    user = db.users.find_one({ "_id": userID })
    if not user:
        raise ValueError("No user found with that ID")
    if user.get("hasAccess"):
        raise ValueError("User already has access — no need to request it again")
    
    request = {
        "email": user["email"],
        "userID": user["_id"]
    }
    try:
        result = db.accessRequests.insert_one(request)
        return {"_id": result.inserted_id}
    except DuplicateKeyError as e:
        raise ValueError("That user is already requesting access") from e

# remove users request from accessRequests
def deny_access(userID):
    # ensure userID is of ObjectId
    if not isinstance(userID, ObjectId):
        userID = ObjectId(userID)
    
    result = db.accessRequests.delete_one({"userID": userID})
    if result.deleted_count:
        return {"deleted_count": result.deleted_count}
    else:
        raise ValueError("No access request found for that userID")

# set hasAccess to True, remove users request from accessRequests
def accept_access(userID):
    # ensure userID is of ObjectId
    if not isinstance(userID, ObjectId):
        userID = ObjectId(userID)
    
    req = db.accessRequests.find_one({"userID": userID})
    if not req:
        raise ValueError("No access request found for that userID")
    
    update_result = db.users.update_one(
        { "_id": userID },
        { "$set": { "hasAccess": True } }
    )
    if update_result.matched_count == 0:
        raise ValueError("No user found with that ID")
    
    # add accepted user to student history
    user = db.users.find_one(
        { "_id": userID },
        { "email":1, "firstName":1, "lastName":1, "courseInfo":1 }
    )
    db.studentHistory.update_one(
        { "userID": userID },
        {
            "$setOnInsert": {
                "userID":    userID,
                "email":     user["email"],
                "firstName": user.get("firstName"),
                "lastName":  user.get("lastName")
            },
            # always push courses into an array and recent accept time
            "$push": {
                "history": {
                    "courseInfo": user.get("courseInfo", []),
                    "acceptedOn": datetime.utcnow()
                }
            }
        },
        upsert=True
    )
    
    delete_result = db.accessRequests.delete_one({ "userID": userID })
    
    return {
        "updated_count": update_result.modified_count,
        "deleted_count": delete_result.deleted_count
    }
    
def generate_api_key(userID):
    # ensure userID is of ObjectId
    if not isinstance(userID, ObjectId):
        userID = ObjectId(userID)
    
    # check if user has access to API keys / exists
    user = db.users.find_one(
        { "_id": userID },
        { "hasAccess": 1, "isAdmin": 1 }
    )
    if not user:
        raise ValueError(f"No user found with ID {userID!r}")
    if not (user.get("isAdmin", False) or user.get("hasAccess", False)):
        raise PermissionError("User does not have access and cannot be issued an API key")
    
    # delete APIkey entry before creating 
    db.APIkeys.delete_one({"userID": userID})
    
    now = datetime.utcnow()
    new_key = {
        "userID":    userID,
        "createdOn": now,
        "updatedOn": now
    }
    try:
        result = db.APIkeys.insert_one(new_key)
        return str(result.inserted_id)
    except PyMongoError as e:
        raise RuntimeError(f"Failed to create API key: {e}") from e
        

if __name__ == "__main__":
    while(True):
        print("""
            Choose an action:
            1) Register a new user
            2) request access for the user
            3) deny access
            4) accept access
            5) flush entries
            6) remove user
            7) generate key for user
            q) Exit
        """)
        choice = input("Enter 1–7/q: ").strip()
        
        if choice == "1":
            doc = {
                "email": "emailtest@kent.edu",
                "courseInfo": [
                    {
                        "CRN": "12345",
                        "courseID": "CS101",
                        "term": "Fall2025"
                    }
                ],
                "firstName": "Alice",
                "lastName": "Smith",
                "isAdmin": False,
                "hasAccess": False
            }
            print("attempting to register user...")
            result = register_user(doc)
            
            new_user = db.users.find_one({ "email": "emailtest@kent.edu" })
            print(new_user)
            
        elif choice == "2":
            print("attempting to request access...")
            new_user = db.users.find_one({ "email": "emailtest@kent.edu" })
            result = request_access(new_user["_id"])
            request_id = result["_id"]
            
            request = db.accessRequests.find_one({ "_id": request_id })
            print(request)
            
        elif choice == "3":
            print("attempting to deny access...")
            new_user = db.users.find_one({ "email": "emailtest@kent.edu" })
            result = deny_access(new_user["_id"])
            
            print(result)
            
        elif choice == "4":
            print("attempting to accept access...")
            new_user = db.users.find_one({ "email": "emailtest@kent.edu" })
            result = accept_access(new_user["_id"])
            
            print(result)
        
        elif choice == "5":
            print("attempting to delete all entries...")
            users_result    = db.users.delete_many({})
            requests_result = db.accessRequests.delete_many({})
            keys_result = db.APIkeys.delete_many({})
            SH_result = db.studentHistory.delete_many({})

            print(f"  • Deleted {users_result.deleted_count} user documents")
            print(f"  • Deleted {requests_result.deleted_count} access request documents")
            print(f"  • Deleted {keys_result.deleted_count} API keys")
            print(f"  • Deleted {SH_result.deleted_count} history documents")
        
        elif choice == "6":
            print("attempting to remove user...")
            new_user = db.users.find_one({ "email": "emailtest@kent.edu" })
            result = remove_user(new_user["_id"])
            
            print(result)
            
        elif choice == "7":
            print("attempting to generate key...")
            new_user = db.users.find_one({ "email": "emailtest@kent.edu" })
            result = generate_api_key(new_user["_id"])
            
            key = db.APIkeys.find_one({ "userID": new_user["_id"] })
            print(key)
        
        elif choice == "q":
            print("exiting...")
            break
        else:
            print("Invalid choice, please enter 1–5/q")