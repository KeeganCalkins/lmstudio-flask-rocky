import os
import lmstudio as lms
from dotenv import load_dotenv
from dataclasses import dataclass

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


def chat(currentRequest: ChatRequest):
    if not currentRequest.stream:
        return chatOneOut(currentRequest)
    return chatStream(currentRequest)

def chatOneOut(currentRequest: ChatRequest):
        # System prompt / user prompt
        chat = lms.Chat(currentRequest.system_message)
        chat.add_user_message(currentRequest.user_message)

        config = {
            "temperature": currentRequest.temperature if currentRequest.temperature is not None else DEFAULT_TEMP,
        }
        if currentRequest.max_tokens is not None:
            config["maxTokens"] = currentRequest.max_tokens

        with lms.Client(SERVER_HOST) as client:
            model = client.llm.model(currentRequest.model_name)
            
            assistant_text = model.respond(chat, config=config)
            chat.add_assistant_response(assistant_text)
            
            return assistant_text.content + "\n"
        
            # print()
            # print("Model used:", prediction_stream.model_info.display_name)
            # print("Predicted tokens:", prediction_stream.stats.predicted_tokens_count)
            # print("Time to first token (seconds):", prediction_stream.stats.time_to_first_token_sec)
            # print("Stop reason:", prediction_stream.stats.stop_reason)
            
            

def chatStream(currentRequest: ChatRequest):
        # System prompt / user prompt
        chat = lms.Chat(currentRequest.system_message)
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
        
        assistant_text = "".join(response_fragments)
        chat.add_assistant_response(assistant_text)
                
        # print()
        # print("Model used:", prediction_stream.model_info.display_name)
        # print("Predicted tokens:", prediction_stream.stats.predicted_tokens_count)
        # print("Time to first token (seconds):", prediction_stream.stats.time_to_first_token_sec)
        # print("Stop reason:", prediction_stream.stats.stop_reason) 


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