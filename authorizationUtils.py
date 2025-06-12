import os
import uuid

from dotenv import load_dotenv

load_dotenv()

# dummy api keys for testing
_USERS = {
    os.getenv("USER1_API_KEY"): {
        "_id":     os.getenv("USER1_ID"),
        "username":os.getenv("USER1_NAME")
    },
}
# dummy session token storage for testing
_SESSIONS: dict[str, dict] = {}

# check if api key is a valid key
def validateKey(api_key: str | None) -> dict | None:
    """
    replace with a Mongo query eg.
        return users.find_one({"api_key": api_key})
    """
    if not api_key:
        return None
    return _USERS.get(api_key)

# gets session token from ChatRequest
def getSessionToken(token: str | None, user_id: str) -> str:
    """
    replace with a Mongo query 
    """
    if token:
        sess = _SESSIONS.get(token)
        if sess and sess["user_id"] == user_id:
            return token
        # If token is invalid
        else:
            return None
    # If no token is given
    return createSessionToken(user_id)
# creates and returns session token
def createSessionToken(user_id):
    new_token = uuid.uuid4().hex
    _SESSIONS[new_token] = {"user_id": user_id, "history": []}
    return new_token

# stores messages with corresponding roles to session token 
def addMessageToSession(token: str, role: str, content: str) -> None:
    """
    replace with a Mongo query eg.
        sessions.update_one(
            {"token": token},
            {"$push": {"history": {"role": role, "content": content}}}
        )
    """
    sessionHistory = _SESSIONS[token]
    
    if role == "user":
        sessionHistory["last_user"] = content
    else:
        sessionHistory["last_assistant"] = content
# retrieves messages with corresponding roles from session token 
def getSessionHistory(token: str) -> list[dict]:
    """
    replace with a Mongo query 
    """
    sessionHistory = _SESSIONS.get(token, {})
    messageHistory = []
    
    if "last_user" in sessionHistory:
        messageHistory.append({"role": "user", "content": sessionHistory["last_user"]})
    if "last_assistant" in sessionHistory:
        messageHistory.append({"role": "assistant", "content": sessionHistory["last_assistant"]})
    return messageHistory