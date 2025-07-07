from flask import Flask, request, jsonify, Response, stream_with_context
from loginUtils import (
    register_user,
    request_access,
    deny_access,
    accept_access,
    generate_api_key,
    remove_user
)
from chat import ChatRequest, ChatResponse
from chatQueue import queueChat
from authorizationUtils import validateKey
from loginUtils import db

from bson import ObjectId
from pymongo.errors import PyMongoError

app = Flask(__name__)

@app.route("/")
def homepage():
    return """
    <h1>LM Studio Chat Server</h1>
    <p>POST JSON to <code>/api/chat</code> with keys:
       <code>{"role":"system|user|assistant","context":"…"}</code> objects, plus optional
       <code>model</code>, <code>stream</code>, <code>max_tokens</code>, and <code>temperature</code>.
    </p>
    """

# Get all users info
@app.route("/api/users", methods=["GET"])
def list_users():
    try:
        users = list(db.users.find({}, {
            "_id": 1,
            "email": 1,
            "firstName": 1,
            "lastName": 1,
            "hasAccess": 1,
            "isAdmin": 1,
            "courseInfo": 1
        }))
        for user in users:
            user["_id"] = str(user["_id"])
            first_course = user.get("courseInfo", [{}])[0]
            user["courseID"] = first_course.get("courseID", "N/A")
            user["term"] = first_course.get("term", "N/A")
            user["CRN"] = first_course.get("CRN", "N/A")
        return jsonify(users)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Get all access requests
@app.route("/api/access-requests", methods=["GET"])
def list_access_requests():
    try:
        requests = list(db.accessRequests.find())
        result = []

        for req in requests:
            user = db.users.find_one(
                { "_id": req["userID"] },
                { "firstName": 1, "lastName": 1, "courseInfo": 1 }
            )
            if user:
                result.append({
                    "_id": str(req["_id"]),
                    "userID": str(req["userID"]),
                    "email": req["email"],
                    "firstName": user.get("firstName", ""),
                    "lastName": user.get("lastName", ""),
                    "courseID": user.get("courseInfo", [{}])[0].get("courseID", "N/A")
                })
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Get user info
@app.route("/api/users/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        oid = ObjectId(user_id)
        user = db.users.find_one({ "_id": oid }, {"hasAccess": 1, "email": 1})
        if not user:
            return jsonify({"error": "User not found"}), 404
        user["_id"] = str(user_id)
        return jsonify(user)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Create new user
@app.route("/api/users", methods=["POST"])
def api_register_user():
    try:
        user_json = request.get_json()
        out = register_user(user_json)
        # turn ObjectId to string
        out["_id"] = str(out["_id"])
        return jsonify(out), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except PyMongoError as e:
        return jsonify({"error": "DB error: " + str(e)}), 500

# Delete user
@app.route("/api/users/<user_id>", methods=["DELETE"])
def api_remove_user(user_id):
    try:
        # validate ObjectId type
        oid = ObjectId(user_id)
        out = remove_user(oid)
        return jsonify(out)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except PyMongoError as e:
        return jsonify({"error": "DB error: " + str(e)}), 500
    
# Request access
@app.route("/api/users/<user_id>/access", methods=["POST"])
def api_request_access(user_id):
    try:
        oid = ObjectId(user_id)
        out = request_access(oid)
        out["_id"] = str(out["_id"])
        return jsonify(out), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PyMongoError as e:
        return jsonify({"error": "DB error: " + str(e)}), 500
    
# Deny access request
@app.route("/api/users/<user_id>/access", methods=["DELETE"])
def api_deny_access(user_id):
    try:
        oid = ObjectId(user_id)
        out = deny_access(oid)
        return jsonify(out)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except PyMongoError as e:
        return jsonify({"error": "DB error: " + str(e)}), 500
    
# Accept access request
@app.route("/api/users/<user_id>/access/accept", methods=["POST"])
def api_accept_access(user_id):
    try:
        oid = ObjectId(user_id)
        out = accept_access(oid)
        return jsonify(out)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except PyMongoError as e:
        return jsonify({"error": "DB error: " + str(e)}), 500

@app.route("/api/users/<user_id>/apikey", methods=["GET"])
def get_api_key(user_id):
    try:
        oid = ObjectId(user_id)
        key = db.APIkeys.find_one({ "userID": oid })
        if not key:
            return jsonify({ "api_key": None }), 200
        return jsonify({ "api_key": str(key["_id"]) }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Generate / rotate API key
@app.route("/api/users/<user_id>/apikey", methods=["POST"])
def api_generate_api_key(user_id):
    try:
        oid = ObjectId(user_id)
        new_key = generate_api_key(oid)
        return jsonify({"api_key": new_key}), 201
    except (ValueError, PermissionError) as e:
        return jsonify({"error": str(e)}), 403
    except PyMongoError as e:
        return jsonify({"error": "DB error: " + str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat_stream_route():
    api_key = request.headers.get("X-API-Key")
    user = validateKey(api_key)
    # if the key was not validated, the user will be None
    # and return error code 401
    if user is None:
        return Response("Unauthorized", status=401)
    
    # client_session_token = request.headers.get("X-Session-Token")
    # session_token = getSessionToken(client_session_token)
    # # if the token was not valid, return error code 401
    # if (session_token == None):
    #     return Response("Invalid session token", status=401)
    
    data = request.get_json() or {}
    # msgs = data.get("messages", [])
    currentRequest = ChatRequest(
        messages       = data.get("messages", []),
        stream         = data.get("stream", False),
        model_name     = data.get("model"),
        max_tokens     = data.get("max_tokens"),
        temperature    = data.get("temperature"),
        #session_token  = session_token,
    )
    
    result = queueChat(currentRequest)
    
    if not currentRequest.stream:
        if isinstance(result, ChatResponse):
            body = result.text
            resp = Response(body, mimetype="text/plain")
            resp.headers["X-Model"]            = result.usage.model_name
            resp.headers["X-Predicted-Tokens"] = str(result.usage.predicted_tokens)
            resp.headers["X-Time-To-First"]    = str(result.usage.time_to_first_token)
            return resp
        else:
            # error in working thread
            return Response(str(result), status=500, mimetype="text/plain")
    
    # response used for streamed responses
    def generate_bytes():
        for chunk in result:
            yield chunk.encode("utf-8")

    resp = Response(
        stream_with_context(generate_bytes()),
        content_type="application/x-ndjson",
        direct_passthrough=True
    )
    # resp.headers["X-Session-Token"] = session_token
    return resp

if __name__ == "__main__":
    app.run(debug=True)
