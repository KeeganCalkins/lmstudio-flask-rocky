from pymongo import MongoClient
import sys

def test_mongodb_connection():
    try:
        # Try to connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        
        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')
        print("Successfully connected to MongoDB!")
        
        # Test database creation
        db = client['test_db']
        collection = db['test_collection']
        
        # Test insert
        test_doc = {"test": "connection"}
        collection.insert_one(test_doc)
        print("Successfully inserted test document!")
        
        # Test read
        result = collection.find_one({"test": "connection"})
        print(f"Successfully retrieved document: {result}")
        
        # Clean up
        collection.delete_one({"test": "connection"})
        print("Successfully cleaned up test data!")
        
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing MongoDB connection...")
    success = test_mongodb_connection()
    sys.exit(0 if success else 1) 