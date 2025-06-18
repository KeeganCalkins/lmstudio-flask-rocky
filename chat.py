import os
import lmstudio as lms
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from models import create_session, get_session, save_message, get_chat_history
from config import SERVER_HOST, DEFAULT_TEMPERATURE

load_dotenv()
SERVER_HOST_WS = SERVER_HOST.replace("http://", "")
DEFAULT_TEMP = 0.6

@dataclass
class ChatRequest:
    system_message: str = "You are a resident AI philosopher."
    user_message: str = "Answer What is the meaning of life? in 100 words or less."
    stream: bool = False
    model_name: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    session_token: Optional[str] = None

def get_or_create_session(session_token: Optional[str], system_message: str) -> str:
    """Get existing session or create new one."""
    if session_token:
        session = get_session(session_token)
        if session:
            return session_token
    
    # Create new session if token doesn't exist or is invalid
    return create_session(system_message)

def chat(currentRequest: ChatRequest):
    # Get or create session
    session_id = get_or_create_session(currentRequest.session_token, currentRequest.system_message)
    
    # Save user message
    save_message(session_id, "user", currentRequest.user_message)
    
    # Get chat history
    chat_history = get_chat_history(session_id)
    
    if not currentRequest.stream:
        return chatOneOut(currentRequest, session_id, chat_history)
    return chatStream(currentRequest, session_id, chat_history)

def chatOneOut(currentRequest: ChatRequest, session_id: str, chat_history: List[Dict[str, Any]]):
    # Create chat with history
    chat = lms.Chat(currentRequest.system_message)
    
    # Add chat history
    for message in chat_history:
        if message["role"] == "user":
            chat.add_user_message(message["content"])
        else:
            chat.add_assistant_response(message["content"])
    
    # Add current user message
    chat.add_user_message(currentRequest.user_message)

    config = {
        "temperature": currentRequest.temperature if currentRequest.temperature is not None else DEFAULT_TEMP,
    }
    if currentRequest.max_tokens is not None:
        config["maxTokens"] = currentRequest.max_tokens

    with lms.Client(SERVER_HOST_WS) as client:
        model = client.llm.model(currentRequest.model_name)
        
        assistant_text = model.respond(chat, config=config)
        chat.add_assistant_response(assistant_text)
        
        # Save assistant response
        save_message(session_id, "assistant", assistant_text.content)
        
        return {
            "session_token": session_id,
            "response": assistant_text.content + "\n"
        }

def chatStream(currentRequest: ChatRequest, session_id: str, chat_history: List[Dict[str, Any]]):
    # Create chat with history
    chat = lms.Chat(currentRequest.system_message)
    
    # Add chat history
    for message in chat_history:
        if message["role"] == "user":
            chat.add_user_message(message["content"])
        else:
            chat.add_assistant_response(message["content"])
    
    # Add current user message
    chat.add_user_message(currentRequest.user_message)

    config = {
        "temperature": currentRequest.temperature if currentRequest.temperature is not None else DEFAULT_TEMP,
    }
    if currentRequest.max_tokens is not None:
        config["maxTokens"] = currentRequest.max_tokens

    with lms.Client(SERVER_HOST_WS) as client:
        model = client.llm.model(currentRequest.model_name)
        prediction_stream = model.respond_stream(chat, config=config)
        
        response_fragments = []
        for fragment in prediction_stream:
            response_fragments.append(fragment.content)
            yield {
                "session_token": session_id,
                "response": fragment.content
            }
        
        # Save complete assistant response
        complete_response = "".join(response_fragments)
        save_message(session_id, "assistant", complete_response)
        
        yield {
            "session_token": session_id,
            "response": "\n"
        }

if __name__ == "__main__":
    TEST_STREAM = True
    TEST_MODEL = "google/gemma-3-12b"
    TEST_SYSTEM = "You are a test bot"
    TEST_USER = "Tell me a 100-word joke."
    currentRequest = ChatRequest(TEST_SYSTEM, TEST_USER, TEST_STREAM)
    
    if currentRequest.stream:
        # Streaming 
        generation = chat(currentRequest)
        print("\n[chat.py] → Streaming result:\n")
        for chunk in generation:
            print(chunk["response"], end="", flush=True)
        print()
    else:
        # Non-streaming 
        result = chat(currentRequest)
        print("\n[chat.py] → Non‐streaming result:\n")
        print(result["response"])