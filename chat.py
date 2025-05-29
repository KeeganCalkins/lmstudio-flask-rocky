import os
import lmstudio as lms
from dotenv import load_dotenv

load_dotenv()
DEFAULT_TEMP=0.6
SERVER_HOST=os.getenv("SERVER_API_HOST")

def chat(
        system_message: str = "You are a resident AI philosopher.",
        user_message:   str = "Answer What is the meaning of life? in 100 words or less.",
        model_name:     str | None = None,
        max_tokens:     int | None = None,
        temperature:    float    | None = None,
    ):
        # System prompt - flask output
        chat = lms.Chat(system_message)
        # User input prompt - flask output
        chat.add_user_message(user_message)

        # User input configs - flask output
        # I dont know exactly what configs we need
        config = {
            "temperature": temperature if temperature is not None else DEFAULT_TEMP,
        }
        if max_tokens is not None:
            config["maxTokens"] = max_tokens

        with lms.Client(SERVER_HOST) as client:
            model = client.llm.model(model_name)
            prediction_stream = model.respond_stream(chat, config=config)

            for fragment in prediction_stream:
                print(fragment.content, end="", flush=True)        
        print()
        print()

        print("Model used:", prediction_stream.model_info.display_name)
        print("Predicted tokens:", prediction_stream.stats.predicted_tokens_count)
        print("Time to first token (seconds):", prediction_stream.stats.time_to_first_token_sec)
        print("Stop reason:", prediction_stream.stats.stop_reason)


if __name__ == "__main__":
    chat()