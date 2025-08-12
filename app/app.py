from flask import Flask, request, jsonify, Response, stream_with_context, g
from loginUtils import (
    register_user,
    request_access,
    deny_access,
    accept_access,
    generate_api_key,
    remove_user,
    revoke_access,
    set_admin
)
from chat import ChatRequest, ChatResponse
from chatQueue import queueChat
from authorizationUtils import validateKey, to_oid, self_or_admin
from loginUtils import db

from bson import ObjectId
from pymongo.errors import PyMongoError

from auth import token_required, admin_required

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
@token_required
@admin_required
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
@token_required
@admin_required
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
                    "courseInfo": user.get("courseInfo", [])
                })
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# return users' history list
@app.route("/api/history", methods=["GET"])
@token_required
@admin_required
def list_history():
    try:
        docs = db.studentHistory.find({})
        result = []
        for doc in docs:
            # build one combined courseInfo array
            courses = []
            for entry in doc.get("history", []):
                courses.extend(entry.get("courseInfo", []))
            result.append({
                "_id":        str(doc["_id"]),
                "userID":     str(doc["userID"]),
                "email":      doc["email"],
                "firstName":  doc.get("firstName"),
                "lastName":   doc.get("lastName"),
                "courseInfo": courses
            })
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error("Failed to list history: %s", e)
        return jsonify({"error": str(e)}), 500

# Get user info
@app.route("/api/users/<user_id>", methods=["GET"])
@token_required
@admin_required
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

@app.route("/api/me", methods=["GET"])
@token_required
def api_get_me():
    claims = g.user_claims
    try:
        me = db.users.find_one(
            { "azureOID": claims["oid"] },
            { "_id":1, "email":1, "hasAccess":1, "isAdmin":1, "courseInfo":1 }
        )
        if not me:
            return jsonify({"error":"Not found"}), 404
        me["_id"] = str(me["_id"])
        return jsonify(me)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Create new user
@app.route("/api/users", methods=["POST"])
@token_required
def api_register_user():
    claims = g.user_claims
    oid    = claims["oid"]
    email  = claims.get("preferred_username") or claims.get("upn") or claims.get("email")
    if not email:
        return jsonify({"error":"No email claim"}), 400

    payload = request.get_json() or {}

    user_json = {
        "azureOID":  oid,
        "email":     email,
        "firstName": payload.get("firstName"),
        "lastName":  payload.get("lastName"),
        "hasAccess": False,
        "isAdmin":   False,
        "courseInfo": payload.get("courseInfo") or [{
            "CRN": "TBD", "courseID":"TBD", "term":"TBD"
        }]
    }
        
    existing = db.users.find_one({"azureOID": oid})
    if existing:
        return jsonify({"_id": str(existing["_id"]) }), 200
    try:
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
@token_required
@admin_required
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
@token_required
def api_request_access(user_id):
    allowed, _ = self_or_admin(user_id)
    if not allowed:
        return jsonify({"error":"Forbidden"}), 403
    try:
        oid = to_oid(user_id)
        payload = request.get_json() or {}
        courses = payload.get("courses")
        
        if courses and isinstance(courses, list):
            db.users.update_one(
                {"_id": oid},
                {"$set": {"courseInfo": courses}}
            )
        
        out = request_access(oid)
        out["_id"] = str(out["_id"])
        return jsonify(out), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PyMongoError as e:
        return jsonify({"error": "DB error: " + str(e)}), 500
    
def _sanitize_courses(courses):
    clean = []
    for c in courses:
        try:
            CRN  = str(c["CRN"])
            cid  = str(c["courseID"])
            term = str(c["term"])
        except (KeyError, TypeError):
            continue
        clean.append({"CRN": CRN, "courseID": cid, "term": term})
    return clean

# toggle admin
@app.route("/api/users/<user_id>/admin", methods=["POST", "DELETE"])
@token_required
@admin_required
def api_admin_toggle(user_id):
    try:
        # Prevent an admin from removing their own admin status
        if request.method == "DELETE":
            me = db.users.find_one({"azureOID": g.user_claims["oid"]}, {"_id": 1})
            if me and str(me["_id"]) == user_id:
                return jsonify({"error": "You cannot remove your own admin status."}), 400

        make_admin = request.method == "POST"
        result = set_admin(user_id, make_admin)
        return jsonify({"_id": user_id, **result}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except PyMongoError as e:
        return jsonify({"error": "DB error: " + str(e)}), 500
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Revoke access
@app.route("/api/users/<user_id>/access/revoke", methods=["POST"])
@token_required
@admin_required
def api_revoke_access(user_id):
    try:
        result = revoke_access(user_id)
        return jsonify({"_id": user_id, **result}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except PyMongoError as e:
        return jsonify({"error": "DB error: " + str(e)}), 500
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Used to check if request is pending
@app.route("/api/users/<user_id>/access/pending", methods=["GET"])
@token_required
def access_pending(user_id):
    allowed, _ = self_or_admin(user_id)
    if not allowed:
        return jsonify({"error":"Forbidden"}), 403
    try:
        oid = to_oid(user_id)
        # See if there is a request in the accessRequests collection
        pending = db.accessRequests.find_one({"userID": oid}) is not None
        return jsonify({"pending": pending}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
# Deny access request
@app.route("/api/users/<user_id>/access", methods=["DELETE"])
@token_required
@admin_required
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
@token_required
@admin_required
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
@token_required
def get_api_key(user_id):
    allowed, _ = self_or_admin(user_id)
    if not allowed:
        return jsonify({"error":"Forbidden"}), 403
    try:
        oid = to_oid(user_id)
        target = db.users.find_one(
            {"_id": oid},
            {"hasAccess":1, "isAdmin":1}
        )
        if not (target and (target.get("hasAccess") or target.get("isAdmin"))):
            return jsonify({"error":"You do not have access"}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    key = db.APIkeys.find_one({"userID": oid})
    return jsonify({"api_key": str(key["_id"]) if key else None}), 200

# Generate / rotate API key
@app.route("/api/users/<user_id>/apikey", methods=["POST"])
@token_required
def api_generate_api_key(user_id):
    claims = g.user_claims
    oid   = claims["oid"]
    me = db.users.find_one({ "azureOID": oid }, {"_id":1, "isAdmin":1})
    if not me:
        return jsonify({"error":"User not found"}), 404
    is_self = str(me["_id"]) == user_id
    if not (me.get("isAdmin") or is_self):
        return jsonify({"error":"Forbidden"}), 403
    
    try:
        target_oid = ObjectId(user_id)
    except:
        return jsonify({"error":"Invalid user_id"}), 400
    
    target = db.users.find_one(
        {"_id": target_oid},
        {"hasAccess":1, "isAdmin":1}
    )
    if not (target and (target.get("hasAccess") or target.get("isAdmin"))):
        return jsonify({"error":"You do not have access"}), 403
    
    try:
        new_key = generate_api_key(target_oid)
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
    
    data = request.get_json() or {}
    currentRequest = ChatRequest(
        messages       = data.get("messages", []),
        stream         = data.get("stream", False),
        model_name     = data.get("model"),
        max_tokens     = data.get("max_tokens"),
        temperature    = data.get("temperature"),
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
    return resp

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error":"Unauthorized"}), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error":"Forbidden"}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8056, debug=True)
