# lmstudio-flask-test
current example input:<br>
```
> python app.py

> curl -N -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -H "X-API-Key: $API_KEY" \
     -d '{
           "system_message": "You are a helpful assistant.",
           "message": "Tell me a short story about boats, 200 words or less",
           "model": "google/gemma-3-4b",
           "stream": true
         }'

> curl -i -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -H "X-API-Key: $API_KEY" -H "X-Session-Token: $Session-Token" \
     -d '{
           "system_message": "You are a helpful assistant.",
           "message": "What did i previously ask?",
           "model": "google/gemma-3-4b",
           "stream": false
         }'

> curl -N -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -H "X-API-Key: $API_KEY" -H "X-Session-Token: $Session-Token" \
     -d '{
           "system_message": "You are a helpful assistant.",
           "message": "What is the best boat to buy? respond in 200 words or less",
           "model": "google/gemma-3-4b",
           "stream": true
        }'
```