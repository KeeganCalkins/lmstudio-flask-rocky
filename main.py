import os
import lmstudio as lms
from dotenv import load_dotenv

load_dotenv()

def chat():
    with lms.Client(os.getenv("SERVER_API_HOST")) as client:
        model = client.llm.model("gemma-3-12b-it")

        # System prompt (will replace with flask output)
        chat = lms.Chat("You are a resident AI philosopher.")
        # User input prompt (will replace with flask output)
        chat.add_user_message("Answer What is the meaning of life? in 100 words or less.")

        # I dont know exactly what configs we need
        prediction_stream = model.respond_stream(chat,  config={
                                                            "temperature": 0.6,
                                                        })
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