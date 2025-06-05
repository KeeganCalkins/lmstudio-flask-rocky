from flask import Flask, request, Response
from chat import chat

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

    result = chat(
        system_message=system_msg,
        user_message=user_msg,
        stream=chat_strm,
        model_name=data.get("model"),
        max_tokens=data.get("max_tokens"),
        temperature=data.get("temperature"),
    )
    return Response(result, mimetype="text/plain")


if __name__ == "__main__":
    app.run(debug=True)
