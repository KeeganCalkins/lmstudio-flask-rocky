import os
import lmstudio as lms
from dotenv import load_dotenv

load_dotenv()
DEFAULT_TEMP=0.6
SERVER_HOST=os.getenv("SERVER_API_HOST")
def chat(
        system_message: str = "You are a resident AI philosopher.",
        user_message:   str = "Answer What is the meaning of life? in 100 words or less.",
        stream:         bool = False,
        model_name:     str | None = None,
        max_tokens:     int | None = None,
        temperature:    float    | None = None,
    ):
    if not stream:
        return chatOneOut(system_message, user_message, model_name, max_tokens, temperature)
    return chatStream(system_message, user_message, model_name, max_tokens, temperature)

def chatOneOut(
        system_message: str,
        user_message:   str,
        model_name:     str,
        max_tokens:     int,
        temperature:    float,
    ):
        # System prompt / user prompt
        chat = lms.Chat(system_message)
        chat.add_user_message(user_message)

        config = {
            "temperature": temperature if temperature is not None else DEFAULT_TEMP,
        }
        if max_tokens is not None:
            config["maxTokens"] = max_tokens

        with lms.Client(SERVER_HOST) as client:
            model = client.llm.model(model_name)
            prediction_stream = model.respond(chat, config=config)
            return prediction_stream.content + "\n"
        
            # print()
            # print("Model used:", prediction_stream.model_info.display_name)
            # print("Predicted tokens:", prediction_stream.stats.predicted_tokens_count)
            # print("Time to first token (seconds):", prediction_stream.stats.time_to_first_token_sec)
            # print("Stop reason:", prediction_stream.stats.stop_reason)
            
            

def chatStream(
        system_message: str,
        user_message:   str,
        model_name:     str,
        max_tokens:     int,
        temperature:    float,
    ):
        # System prompt / user prompt
        chat = lms.Chat(system_message)
        chat.add_user_message(user_message)

        config = {
            "temperature": temperature if temperature is not None else DEFAULT_TEMP,
        }
        if max_tokens is not None:
            config["maxTokens"] = max_tokens

        with lms.Client(SERVER_HOST) as client:
            model = client.llm.model(model_name)
            prediction_stream = model.respond_stream(chat, config=config)
            for fragment in prediction_stream:
                yield fragment.content 
            yield "\n"
                
            # print()
            # print("Model used:", prediction_stream.model_info.display_name)
            # print("Predicted tokens:", prediction_stream.stats.predicted_tokens_count)
            # print("Time to first token (seconds):", prediction_stream.stats.time_to_first_token_sec)
            # print("Stop reason:", prediction_stream.stats.stop_reason) 


if __name__ == "__main__":
    TEST_STREAM = False
    TEST_MODEL  = "google/gemma-3-12b"
    TEST_SYSTEM = "You are a test bot"
    TEST_USER   = "Tell me a 100-word joke."
    
    if TEST_STREAM:
        # Streaming 
        generation = chat(
            system_message=TEST_SYSTEM,
            user_message=TEST_USER,
            stream=True,
            model_name=TEST_MODEL,
        )
        print("\n[chat.py] → Streaming result:\n")
        for chunk in generation:
            print(chunk, end="", flush=True)
        print()
    else:
        # Non-streaming 
        text = chat(
            system_message=TEST_SYSTEM,
            user_message=TEST_USER,
            stream=False,
            model_name=TEST_MODEL,
        )
        print("\n[chat.py] → Non‐streaming result:\n")
        print(text)