# lmstudio-flask-test
current example input:<br>
```
> python app.py

> curl -N -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "system_message": "You are a helpful assistant.",
           "message": "Tell me a short story about boats, 200 words or less",
           "model": "google/gemma-3-4b",
           "stream": true,
           "max_tokens": 50,
           "temperature": 0.7
         }'

> curl -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "system_message": "You are a helpful assistant.",
           "message": "Tell me a haiku about autumn.",                       
           "model": "google/gemma-3-4b",
           "stream": false,
           "max_tokens": 50,
           "temperature": 0.7
         }'

> curl -N -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "system_message": "You are a helpful assistant.",
           "message": "What is the best boat to buy? respond in 200 words or less",
           "model": "google/gemma-3-4b",
           "stream": true
        }'
```