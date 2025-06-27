import os
import uuid
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

load_dotenv()

# Mongo connection
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# add user to users collection with unique email
def register_user(doc):
    try:
        result = db.users.insert_one(doc)
        return {"_id": result.inserted_id}
    except DuplicateKeyError as e:
        raise ValueError("That email is already registered") from e

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
    delete_result = db.accessRequests.delete_one({ "userID": userID })
    
    return {
        "updated_count": update_result.modified_count,
        "deleted_count": delete_result.deleted_count
    }

if __name__ == "__main__":
    while(True):
        print("""
            Choose an action:
            1) Register a new user
            2) request access for the user
            3) deny access
            4) accept access
            5) flush entries
            q) Exit
        """)
        choice = input("Enter 1–5/q: ").strip()
        
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

            print(f"  • Deleted {users_result.deleted_count} user documents")
            print(f"  • Deleted {requests_result.deleted_count} access request documents")
        
        elif choice == "q":
            print("exiting...")
            break
        else:
            print("Invalid choice, please enter 1–5/q")