#port for this server : 3000
from fastapi import FastAPI
import requests
from utilshandlers.request_handler import request_handler, request_handler_get
from pydantic import BaseModel

app = FastAPI()

BaseUrl = "http://127.0.0.1:4000/api/"

class Item(BaseModel):
    key: str
    summary: bool = False


@app.post("/api/gpt-agent")
def gpt_agent(args: Item):
    try:
        if not args.summary:
            gptResponse = request_handler(BaseUrl + "gpt", {'key': args.key})
            return gptResponse
        else:
            print("Summarizing chat history")
            gptResponse = request_handler_get(BaseUrl + "summarize")
            return gptResponse
    except Exception as e:
        print(e)

@app.get("/api/alive")
def check_alive_status():
    print(":::::::;check live staus::::::::::::::::")
    check_status_response = request_handler_get(BaseUrl + "alive")

    if check_status_response != False:
        return {"alive": True}
    return {"alive": False}