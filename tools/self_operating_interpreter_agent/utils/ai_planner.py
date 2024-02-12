import requests
from operate.operate import thought_history

chat_history = []
CHAT_COMPLETEION_URL = 'https://openai.ru9.workers.dev/v1/chat/completions'

def ai_planner(content):
  chat_history.append({"role":"user","content":content})
  url = CHAT_COMPLETEION_URL
  headers = {
      "Content-Type": "application/json",
  }
  data = {'model': 'gpt-4-1106-preview', 'temperature':0.8,'messages': chat_history}
  response = requests.post(url, headers=headers, json=data)
  assistant_reply = response.json()['choices'][0]['message']['content']
  chat_history.append({"role": "system", "content": assistant_reply})
  return {'result': response.json()['choices'][0]['message']['content']}

thought_history.append({"role":"system","content": "You are a AI orchestrator, You will answer the last asked question by user from the user and assistant history in summarised form."})

def summarize_chat_history(content):
    thought_history.append({"role":"user","content":content})
    print(':::::::::::thought_history::::::::::::::',thought_history)
    print('chat_history:',thought_history)
    url = "https://openai.ru9.workers.dev/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
    }
    data = {'model': 'gpt-4-1106-preview', 'messages': thought_history, 'temperature':0.5}
    response = requests.post(url, headers=headers, json=data)
    return {'result': response.json()['choices'][0]['message']['content']}
  
  
