# lmstudio-flask-test

## Python Usage Example
```python
from chat import ChatRequest, chat

# Create a new chat session
request = ChatRequest(
    system_message="You are a helpful assistant",
    user_message="Hello!",
    session_token=None  # Will create new session
)

# Get response
result = chat(request)
print(f"Session token: {result['session_token']}")
print(f"Response: {result['response']}")

# Continue conversation with the same session
follow_up_request = ChatRequest(
    system_message="You are a helpful assistant",
    user_message="Tell me more about that",
    session_token=result['session_token']  # Use the session token from previous response
)
```

## API Usage Examples
current example input:<br>
```
> python app.py

curl http://localhost:1234/v1/chat/completions \  -H "Content-Type: application/json" \  -d '{    "model": "deepseek-r1-distill-qwen-7b",    "messages": [      { "role": "system", "content": "Always answer in rhymes. Today is Thursday" },      { "role": "user", "content": "What day is it today?" }    ],    "temperature": 0.7,    "max_tokens": -1,    "stream": false}'


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