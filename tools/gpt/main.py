#port for this server : 4000

from fastapi import FastAPI
import requests
app = FastAPI()
chat_history = []
from pydantic import BaseModel

chat_history = []

chat_history.append({"role": "system", "content": """You are an AI assistant who when given a Input you will
                    - First Read and understand the request to see if its relevant
                    - Understand the request data and create a plan for it 
                    - Once you think the task as completed, Give response 'End_Conversation' and nothing else."""})

class Item(BaseModel):
    key: str


@app.post("/api/gpt")
def open_ai_main(mesaage: Item):
    try:
        chat_history.append({"role":"user","content":mesaage.key})
        url = "https://openai.ru9.workers.dev/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
        }
        data = {'model': 'gpt-4-1106-preview', 'messages': chat_history}
        response = requests.post(url, headers=headers, json=data)
        assistant_reply = response.json()['choices'][0]['message']['content']
        chat_history.append({"role": "assistant", "content": assistant_reply})
        return {'result': response.json()['choices'][0]['message']['content']}
    except Exception as e:
        print(":::open_ai_main::: ERROR::",e)
        return {'result': 'Error'}
    

@app.get("/api/summarize")
def summarize_chat_history():
    try:
        chat_history_clone = chat_history[:]
        chat_history_clone.append({"role":"assistant","content":"Summarize the provided chat history"})
        url = "https://openai.ru9.workers.dev/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
        }
        data = {'model': 'gpt-4-1106-preview', 'messages': chat_history_clone, 'temperature':0.5}
        response = requests.post(url, headers=headers, json=data)
        assistant_reply = response.json()['choices'][0]['message']['content']
        return {'result': assistant_reply}
    except Exception as e:
        print(":::open_ai_main::: ERROR::",e)
        return {'result': 'Error'}

@app.get("/api/alive")
def check_alive_status():
    return {"alive": True}