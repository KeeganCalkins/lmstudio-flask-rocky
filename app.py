from flask import Flask, request, Response, stream_with_context
from chat import ChatRequest, ChatResponse
from chatQueue import queueChat
from authorizationUtils import validateKey
#from authorizationUtils import ( validateKey, getSessionToken, addMessageToSession )

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
