from flask import Flask, request, Response, jsonify
from chat import ChatRequest
from chatQueue import queueChat

app = Flask(__name__)

@app.route("/")
def homepage():
    return """
    <h1>LM Studio Chat Server</h1>
    <p>POST JSON to <code>/api/chat</code> with keys:
       <code>message</code>, <code>system_message</code>, <code>stream</code> (boolean), etc.
    </p>
    """

@app.route("/api/chat", methods=["POST"])
def chat_stream_route():
    data = request.get_json() or {}
    system_msg  = data.get("system_message", "")
    user_msg    = data.get("message",        "")
    chat_strm = data.get("stream", False)
    currentRequest = ChatRequest(system_msg, user_msg, chat_strm)

    result = queueChat(currentRequest)
    if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
        # Streaming: collect all chunks and return as JSON
        response_chunks = []
        session_token = None
        for chunk in result:
            if isinstance(chunk, dict):
                session_token = chunk.get("session_token", session_token)
                response_chunks.append(chunk.get("response", ""))
        return jsonify({"session_token": session_token, "response": "".join(response_chunks)})
    else:
        # Non-streaming: return as JSON
        return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
