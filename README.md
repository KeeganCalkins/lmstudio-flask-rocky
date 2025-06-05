# lmstudio-flask-test
current example input:<br>
```
python app.py
curl -X POST http://127.0.0.1:5000/api/chat
   -H "Content-Type: application/json"      
   -d '{
         "system_message": "You are an AI assistant that speaks in haiku.",
         "message": "Explain the concept of recursion.",
         "stream": false,
         "model": "google/gemma-3-12b",
         "max_tokens": 60,
         "temperature": 0.7
       }'
```
