# lmstudio-flask-test
current example input:<br>
```
> python app.py

> curl -N -X POST http://localhost:5000/api/chat \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{
        "messages": [
            {"role": "system",    "content": "You are chatbot"},
            {"role": "user",      "content": "How many states"},
            {"role": "assistant", "content": "there be 50 states"},
            {"role": "user",      "content": "what did you just say?"}
        ],
        "model":  "google/gemma-3-12b",
        "stream": true
    }'

    

> curl -i -X POST http://localhost:5000/api/chat \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{
        "messages": [
            {"role": "system",    "content": "You are chatbot"},
            {"role": "user",      "content": "How many states"},
            {"role": "assistant", "content": "there be 50 states"},
            {"role": "user",      "content": "what did you just say?"}
        ],
        "model":  "google/gemma-3-12b",
        "stream": false
    }'
```
