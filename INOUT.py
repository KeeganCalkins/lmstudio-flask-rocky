# from flask import Flask, request, session

# app = Flask(__name__)

# input = {
#     'model': 'default',
#     'base': 'You are an AI assistant',
#     'history': 'default',
#     'prompt': 'default'
# }

# @app.route('/data', methods=['GET', 'POST'])
# def handle_data():
#     global pending_request
    

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/post', methods=['POST'])
def post_data():
    # Get the JSON data from the request
    data = request.get_json()

    # Check if data is a dictionary
    if isinstance(data, dict):
        # Process the data (for example, just return it)
        return jsonify({"status": "success", "data": data}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid data format, expected a dictionary."}), 400
    
# GET endpoint to return a sample dictionary
@app.route('/get', methods=['GET'])
def get_data():
    sample_data = {         #may want to impliment some kind of actual json interaction here, like puttting something in the JSON
        "model": "value1",
        "context": "value2",
        "request": "value3"
    }
    return jsonify({"status": "success", "data": sample_data}), 200

if __name__ == '__main__':
    app.run(debug=True)
