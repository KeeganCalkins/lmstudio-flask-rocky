import os
import lmstudio as lms
from dotenv import load_dotenv
import json
from dataclasses import dataclass
from typing import Generator, Union
from authorizationUtils import ( getSessionHistory, addMessageToSession )

load_dotenv()
DEFAULT_TEMP=0.6
SERVER_HOST=os.getenv("SERVER_API_HOST")

@dataclass
class ChatRequest:
    system_message: str = "You are a resident AI philosopher."
    user_message:   str = "Answer What is the meaning of life? in 100 words or less."
    stream:         bool = False
    model_name:     str | None = None
    max_tokens:     int | None = None
    temperature:    float    | None = None
    session_token:  str = None
    
@dataclass
class ChatUsage:
    model_name:          str
    predicted_tokens:    int
    time_to_first_token: float
    stop_reason:         str


@dataclass
class ChatResponse:
    text:  str
    usage: ChatUsage


def chat(currentRequest: ChatRequest) -> Union[ChatResponse, Generator[str, None, ChatUsage]]:
    if not currentRequest.stream:
        return chatOneOut(currentRequest)
    return chatStream(currentRequest)

def chatOneOut(currentRequest: ChatRequest) -> ChatResponse:
        # system prompt / user prompt
        chat = lms.Chat(currentRequest.system_message)
        # get history from session token
        for msg in getSessionHistory(currentRequest.session_token):
            if msg["role"] == "user":
                chat.add_user_message(msg["content"])
            else:
                chat.add_assistant_response(msg["content"])
            
        chat.add_user_message(currentRequest.user_message)

        config = {
            "temperature": currentRequest.temperature if currentRequest.temperature is not None else DEFAULT_TEMP,
        }
        if currentRequest.max_tokens is not None:
            config["maxTokens"] = currentRequest.max_tokens

        with lms.Client(SERVER_HOST) as client:
            model = client.llm.model(currentRequest.model_name)
            assistant_text = model.respond(chat, config=config)

        # adds/replaces message cache
        addMessageToSession(currentRequest.session_token, "user", currentRequest.user_message)
        addMessageToSession(currentRequest.session_token, "assistant", assistant_text.content)
        
        stats = assistant_text.stats
        usage = ChatUsage(
            model_name          = assistant_text.model_info.display_name,
            predicted_tokens    = stats.predicted_tokens_count,
            time_to_first_token = stats.time_to_first_token_sec,
            stop_reason         = stats.stop_reason,
        )
        
        return ChatResponse(text=assistant_text.content + "\n", usage=usage)

def chatStream(currentRequest: ChatRequest) -> Generator[str, None, ChatUsage]:
        # System prompt / user prompt
        chat = lms.Chat(currentRequest.system_message)
        # get history from session token
        for msg in getSessionHistory(currentRequest.session_token):
            if msg["role"] == "user":
                chat.add_user_message(msg["content"])
            else:
                chat.add_assistant_response(msg["content"])
            
        chat.add_user_message(currentRequest.user_message)

        config = {
            "temperature": currentRequest.temperature if currentRequest.temperature is not None else DEFAULT_TEMP,
        }
        if currentRequest.max_tokens is not None:
            config["maxTokens"] = currentRequest.max_tokens

        with lms.Client(SERVER_HOST) as client:
            model = client.llm.model(currentRequest.model_name)
            prediction_stream = model.respond_stream(chat, config=config)
            
            response_fragments = []
            for fragment in prediction_stream:
                response_fragments.append(fragment.content)
                yield fragment.content 
            yield "\n"
        
        # adds/replaces message cache
        assistant_text = "".join(response_fragments)
        addMessageToSession(currentRequest.session_token, "user", currentRequest.user_message)
        addMessageToSession(currentRequest.session_token, "assistant", assistant_text)
        
        stats = prediction_stream.stats
        payload = {
            "session_token":       currentRequest.session_token,
            "model_name":          prediction_stream.model_info.display_name,
            "predicted_tokens":    stats.predicted_tokens_count,
            "time_to_first_token": stats.time_to_first_token_sec,
            "stop_reason":         stats.stop_reason,
        }
        yield json.dumps({"usage": payload}, indent=4) + "\n"
        # return usage


if __name__ == "__main__":
    TEST_STREAM = True
    TEST_MODEL  = "google/gemma-3-12b"
    TEST_SYSTEM = "You are a test bot"
    TEST_USER   = "Tell me a 100-word joke."
    currentRequest = ChatRequest(TEST_SYSTEM, TEST_USER, TEST_STREAM)
    
    if currentRequest.stream:
        # Streaming 
        generation = chat(currentRequest)
        print("\n[chat.py] → Streaming result:\n")
        for chunk in generation:
            print(chunk, end="", flush=True)
        print()
    else:
        # Non-streaming 
        text = chat(currentRequest)
        print("\n[chat.py] → Non‐streaming result:\n")
        print(text)