import sys
sys.path.append('/Users/abhishekanand/Documents/self-operating-computer')
from operate.operate import main, thought_history
from fastapi import FastAPI
from pydantic import BaseModel
from colorama import init, Fore, Style
from utils.planner import  planner_method
from utils.request_handler import request_handler
 
app = FastAPI()

class Item(BaseModel):
    key: str
    summary: bool = False

SELF_OPERATING_TOOL = "http://127.0.0.1:8002/operate"
@app.post("/self_operating_agent")
def self_operating_planner(message: Item):
    if not message.summary:
        planner_response = planner_method(message.key)
        result = planner_response['result']
        print("::::AGENT PLAN:::::", result)
        request_handler(SELF_OPERATING_TOOL, {"key":result})
    else: 
        print(":::::::INSIDE SELF_OPERATING_AGENT SUMMARY:::::", message.summary)
        summary_response = request_handler(SELF_OPERATING_TOOL, {'key':'', 'summary':message.summary})
        print("::::AGENT SUMMARY:::::", summary_response)
        return {'result': summary_response['result']}