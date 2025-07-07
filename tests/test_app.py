import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from bson import ObjectId
from pymongo import MongoClient
import loginUtils
from app import app

@pytest.fixture(autouse=True)
def clear_database():
    """
    Runs before each test: deletes all docs from the three collections.
    That way each test starts with an empty but schema-ready DB.
    """
    db = loginUtils.db
    for col in ("users", "accessRequests", "APIkeys"):
        # If the collection doesn't exist yet, this is a no-op
        db[col].delete_many({})
    yield
    # (optional) you could also drop indexes here if you wanted to test index
    # creation, but since your schema is live in rockydb, it's unnecessary.

@pytest.fixture
def client():
    return app.test_client()

def test_full_user_lifecycle(client):
    # 1) Register a user
    payload = {
        "email": "jane@kent.edu",
        "courseInfo": [{"CRN":"111","courseID":"TEST101","term":"F2025"}],
        "firstName": "Jane",
        "lastName": "Doe",
        "isAdmin": False,
        "hasAccess": False
    }
    resp = client.post("/api/users", json=payload)
    assert resp.status_code == 201
    uid = resp.get_json()["_id"]

    # 2) Request access
    resp = client.post(f"/api/users/{uid}/access")
    assert resp.status_code == 201

    # 3) Deny access
    resp = client.delete(f"/api/users/{uid}/access")
    assert resp.status_code == 200
    assert resp.get_json()["deleted_count"] == 1

    # 4) Request again & accept access
    client.post(f"/api/users/{uid}/access")
    resp = client.post(f"/api/users/{uid}/access/accept")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["updated_count"] == 1 and data["deleted_count"] == 1

    # 5) Generate API key (user now hasAccess)
    resp = client.post(f"/api/users/{uid}/apikey")
    assert resp.status_code == 201
    key = resp.get_json()["api_key"]
    assert ObjectId(key)  # validates format

    # 6) Delete the user (cascade cleanup)
    resp = client.delete(f"/api/users/{uid}")
    assert resp.status_code == 200
    info = resp.get_json()
    assert info["deleted_user"] == 1
    assert info["deleted_requests"] == 0
    assert info["deleted_api_keys"] == 1

    # 7) Deleting again yields 404
    resp = client.delete(f"/api/users/{uid}")
    assert resp.status_code == 404
