import os
from dotenv import load_dotenv
load_dotenv()
open_intepreter_path = os.getenv("OPEN_INTERPRETER_PATH")
import sys
sys.path.append(open_intepreter_path)
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from interpreter import interpreter
from pydantic import BaseModel
from colorama import init, Fore, Style
from utilshandlers.request_handler import request_handler

app = FastAPI()
# Interpreter setting
interpreter.llm.api_base = "https://openai.ru9.workers.dev/v1"
interpreter.auto_run = True
interpreter.llm.model = "gpt-4-1106-preview"

# Interpreter Persona
interpreter.chat('You are a powerful code executioner which can perform any task assigned to you. If you feel that task which is beyond your capability, You can provide your own solution.')


def interpretor_chat(chat_detail):
    """
    1. A function that interprets the chat details and returns the messages from the interpreter. 
    2. It takes a single parameter 'chat_detail' and returns the messages from the interpreter. 
    3. If an exception occurs, it prints an error message along with the exception.

    """
    try:
        # for chunk in interpreter.chat(chat_detail, stream=True):
        #     if 'format' in chunk and chunk['format'] == 'execution':
        #         return {'value': 'Enter y or n to run your code', 'permission': True}
        interpreter.chat(chat_detail)
        return interpreter.messages
    except Exception as e:
        print("interpretor_chat error", e)


# interpretor_response = interpretor_chat('create a conversation between two people of 4 line')
# interpretor_response_content = interpretor_response[len(interpretor_response)-1]['content']
class Item(BaseModel):
    key: str

@app.post("/api/interpreter")
def interpreter_chat_endpoint(message: Item):
    """
    1. Chat endpoint for the interpreter, takes a message as input and sends it to the interpreter for processing.
    """
    print(f"{Fore.GREEN}{Style.BRIGHT}[OPENAI]{Style.RESET_ALL} {message.key}")
    interpretor_response = interpretor_chat(message.key)
    interpretor_response_content = interpretor_response[len(interpretor_response)-1]['content']
    print(f"{Fore.YELLOW}{Style.BRIGHT}[INTERPRETER]{Style.RESET_ALL} {interpretor_response_content}")
    request_handler("http://localhost:8000/api/openai", {"key": interpretor_response_content, "summary": False})

@app.get("/api/alive")
def check_alive_status():
    return {"alive": True}