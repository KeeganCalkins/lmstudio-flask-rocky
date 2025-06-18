import threading
import queue
from chat import ChatRequest, chatOneOut, chatStream, get_or_create_session, get_chat_history

request_queue = queue.Queue()
    
def runChat():
    while True:
        currentRequest: ChatRequest = request_queue.get()
        try:
            # Get or create session and chat history
            session_id = get_or_create_session(currentRequest.session_token, currentRequest.system_message)
            chat_history = get_chat_history(session_id)
            # not streamed
            currentRequest._response = chatOneOut(currentRequest, session_id, chat_history)
        except Exception as e:
            currentRequest._response = f"ERROR: {e}"
        finally:
            # signal request is finished
            currentRequest._done.set()
            request_queue.task_done()
# start single thread
_thread = threading.Thread(target=runChat, daemon=True)
_thread.start()

# lock used for streaming output
_stream_lock = threading.Lock()
def queueChat(currentRequest: ChatRequest) -> str:
    #print("queued request!")

    if currentRequest.stream:
        # streamed
        def generate():
            # lock used to wait for stream to finish
            with _stream_lock:
                for chunk in chatStream(currentRequest):
                    yield chunk
                #print("completed request!")
        return generate()
    
    # threading.Event for completion sig
    currentRequest._done = threading.Event()
    currentRequest._response = None

    request_queue.put(currentRequest)
    currentRequest._done.wait()      # waits until currentRequest._done.set()
    #print("completed request!")
    return currentRequest._response
