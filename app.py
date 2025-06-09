from flask import Flask, request, Response
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
    return Response(result, mimetype="text/plain")


if __name__ == "__main__":
    app.run(debug=True)
