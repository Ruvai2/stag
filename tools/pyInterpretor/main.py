import os
import threading
from dotenv import load_dotenv
load_dotenv()
# URL = os.getenv("YOUR_AGENT_URL")
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
from utilshandlers.openAiHandler import createChatClient
from utilshandlers.request_handler import request_handler
from utilshandlers.openai_planner import ai_planner_1, ai_planner_2, ai_planner_3, chat_history, summarize_chat_history_and_append, summarize_chat_history
from utilshandlers.openai_planner import ai_solution_marking
from websocket_client import main

# def start_websocket_client(param):
#     thread = Thread(target=lambda: main(text=param))
#     thread.start()
# start_websocket_client("Hy, i'm chat box")
# port 8000
app = FastAPI()
INTERPRETER_URL = "http://127.0.0.1:9001/api/interpreter"

def openai_chat(chat_detail):
    """
    1. Function to interact with OpenAI chat API and return the response.
    
    2. Parameters:
    - chat_detail: a dictionary containing details for the chat
    
    3. Returns:
    - A string representing the response from OpenAI chat API
    - If an exception occurs, it returns a dictionary with a 'content' key containing an error message
    """
    try:
        openai_response = createChatClient(chat_detail)
        return openai_response['result']
    except Exception as e:
        print("openai_chat error", e)
        return {'content': 'Sorry, I am not able to understand you. Please try again.'}

def check_content(content):
    """
    - Check the content for the presence of 'End_Conversation' and return a boolean indicating its presence.
    """
    index = content.find('End_Conversation')
    check = True if index != -1 else False
    return check

class Item(BaseModel):
    key: str
    summary: bool = False
    from_interpreter: bool = False
    
        
@app.post("/api/openai")
def openai_chat_endpoint(message: Item):
    """
     - This function serves as the endpoint for OpenAI chat. 
     - It takes a message as input and executes three AI planners to generate solutions.
     - It then selects the best solution and performs further processing based on the selected planner. If an exception occurs, it returns a message indicating the failure.
    """
    try:
        if not message.summary:
            threading.Thread(target=driver, args=(message,)).start()
        else:
            response_from_summarize_chat_history_and_append = summarize_chat_history_and_append(message.key)
            if response_from_summarize_chat_history_and_append.find('APPEND') != -1:
                threading.Thread(target=request_handler, args=(message,)).start()
                response_from_summarize_chat_history = summarize_chat_history()
                return {"chat_summary": response_from_summarize_chat_history}
            else:
                return {"chat_summary": response_from_summarize_chat_history_and_append}
    except Exception as e:
        print("openai_chat_endpoint error", e)
        # Return a default message in case of any error
        return {'content': 'Sorry, I am not able to understand you. Please try again.'}
    


def driver(message):
    best_solution = []
    planner1_response = ai_planner_1(message.key)
    planner2_response = ai_planner_2(message.key)
    planner3_response = ai_planner_3(message.key)
    planner1_result = ai_solution_marking(planner1_response['result'])
    planner2_result = ai_solution_marking(planner1_response['result'])
    planner3_result = ai_solution_marking(planner1_response['result'])
    # print(":::::::::::Planner1::::::::::::::::::::", planner1_result)
    # print(":::::::::::Planner2::::::::::::::::::::", planner2_result)
    # print(":::::::::::Planner3::::::::::::::::::::", planner3_result)
    best_solution.append({'marks':planner1_result['result'], 'name': 'planner1'})
    best_solution.append({'marks':planner2_result['result'], 'name': 'planner2'})
    best_solution.append({'marks':planner3_result['result'], 'name': 'planner3'})
    max_data = max(best_solution, key=lambda x: x['marks'])
    webhook_url = 'http://0.0.0.0:8080/webhook'
    
    if max_data['name'] == 'planner1':
        check = check_content(planner1_response['result'])
        if check:
            print(":::::::::::::::END_CONVERSATION::::::::::::::::::")
            response_from_summarize_chat_history = summarize_chat_history()
            print(":::::::::::::response_from_summarize_chat_history:::::::::::::", response_from_summarize_chat_history)
            data_to_send = {"key": response_from_summarize_chat_history}
            request_handler(webhook_url, data_to_send)
            return 
        request_handler(INTERPRETER_URL, {"key": planner1_response['result']})
    elif max_data['name'] == 'planner2':
        check = check_content(planner1_response['result'])
        if check: 
            print(":::::::::::::::END_CONVERSATION::::::::::::::::::")
            response_from_summarize_chat_history = summarize_chat_history()
            print(":::::::::::::response_from_summarize_chat_history:::::::::::::", response_from_summarize_chat_history)
            data_to_send = {"key": response_from_summarize_chat_history}
            request_handler(webhook_url, data_to_send)
            return
        request_handler(INTERPRETER_URL, {"key": planner2_response['result']})
    elif max_data['name'] == 'planner3':
        check = check_content(planner1_response['result'])
        if check:
            print(":::::::::::::::END_CONVERSATION::::::::::::::::::")
            response_from_summarize_chat_history = summarize_chat_history()
            print(":::::::::::::response_from_summarize_chat_history:::::::::::::", response_from_summarize_chat_history)
            data_to_send = {"key": response_from_summarize_chat_history}
            request_handler(webhook_url, data_to_send)
            return
        request_handler(INTERPRETER_URL, {"key": planner3_response['result']})


@app.get("/api/alive")
def check_alive_status():
    return {"alive": True}