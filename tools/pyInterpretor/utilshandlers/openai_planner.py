import requests
import random
CHAT_COMPLETEION_URL = "https://openai.ru9.workers.dev/v1/chat/completions"
# chat_history_planner1 = []
# chat_history_planner2 = []
# chat_history_planner3 = []
# ai_solution_marking_point = []
chat_history = []
chat_history.append({
        "role": "system",
        "content": "You are a AI orchestrator, When you get a request from a group of agents and your you will interact with a AI Tool Called Open interpreter which can execute any task // 1. Understand the request and reply back with a plan and what its need to run. And you need to tell it step by step how to do it. // 2. Your responses will be sent to open interpreter, And you will be talking to open interpreter to solve tasks. //3. If you find that the open interpreter is unable to adhere to your request, instruct it to autonomously execute the necessary steps to fulfill the task.//4. Once you think the task as completed, Give response 'End_Conversation' and nothing else."
      })
chat_history.append({
        "role": "user",
        "content": "Hi, this is your first response from the group and after this you will be interacting with Open interpreter and you will be given a task which you need to interact with open Interpretor and complete it."
      })
chat_history.append({
        "role": "assistant",
        "content": "Sure, Thanks for the Information, I understand the from now i am talking to a AI Assistant called 'Open interpreter' and i am waiting for the query once i get the task i will start interacting to complete the task and initially i will just interact with open interpreter directly with the task and later answer its quesions step by step, once i complete it i will give the response End_Conversation"
      })      
def ai_planner_1(content):
  chat_history.append({"role":"user","content":content})

  url = CHAT_COMPLETEION_URL

  headers = {
      "Content-Type": "application/json",
  }
  data = {'model': 'gpt-4-1106-preview','messages': chat_history, "temperature":0.2}
  response = requests.post(url, headers=headers, json=data)
  assistant_reply = response.json()['choices'][0]['message']['content']
  chat_history.append({"role": "system", "content": assistant_reply})
  
  return {'result': assistant_reply}


def ai_planner_2(content):
  chat_history.append({"role":"user","content":content})

  url = CHAT_COMPLETEION_URL
  headers = {
      "Content-Type": "application/json",
  }
  data = {'model': 'gpt-4-1106-preview', 'temperature':0.8,'messages': chat_history}
  response = requests.post(url, headers=headers, json=data)
  assistant_reply = response.json()['choices'][0]['message']['content']
  chat_history.append({"role": "system", "content": assistant_reply})
  # chat_history.pop()
  return {'result': response.json()['choices'][0]['message']['content']}


def ai_planner_3(content):
  chat_history.append({"role":"user","content":content})

  url = CHAT_COMPLETEION_URL
  headers = {
      "Content-Type": "application/json",
  }
  data = {'model': 'gpt-4-1106-preview', 'messages': chat_history, 'temperature':0.5}
  response = requests.post(url, headers=headers, json=data)
  assistant_reply = response.json()['choices'][0]['message']['content']
  chat_history.append({"role": "system", "content": assistant_reply})
  # chat_history.pop()
  return {'result': response.json()['choices'][0]['message']['content']}

def ai_solution_marking(content):
    random_number = random.random()
    result = int(round(random_number))    
    return {'result': result}

# def maintain_chat_history(content):
#     chat_history.append({"role": "system", "content": content})
#     return

def openai_human_conversation(content):
  conversaion_history = chat_history[:]
  conversaion_history.append({"role":"user","content": "Human is asking for a question like this can you answer the question by understanding the past responses:" + content })

  url = CHAT_COMPLETEION_URL
  headers = {
      "Content-Type": "application/json",
  }
  data = {'model': 'gpt-4-1106-preview', 'messages': conversaion_history, 'temperature':0.2}
  response = requests.post(url, headers=headers, json=data)
  assistant_reply = response.json()['choices'][0]['message']['content']
  conversaion_history.append({"role": "system", "content": assistant_reply})
  return {'result': response.json()['choices'][0]['message']['content']}
    

def summarize_chat_history_and_append(content):
    chat_history_clone = chat_history[:]
    chat_history_clone.append({"role":"system","content":"If you perceive that the input aims to make changes or modify the task rather than asking questions about it, simply send the keyword 'APPEND' without additional information. However, if the inquiry pertains to questions about the task, send only the summary of the chat history"})
    chat_history_clone.append({"role":"user","content":content})
    url = "https://openai.ru9.workers.dev/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
    }
    data = {'model': 'gpt-4-1106-preview', 'messages': chat_history_clone, 'temperature':0.5}
    response = requests.post(url, headers=headers, json=data)
    assistant_reply = response.json()['choices'][0]['message']['content']

    index = assistant_reply.find('APPEND')
    if index != -1:
        chat_history.append({"role":"user","content":content})
    else :        
      chat_history.append({"role": "user", "content": content})
      chat_history.append({"role": "system", "content": assistant_reply})
        
    return assistant_reply

def summarize_chat_history():
    chat_history_clone = chat_history[:]
    chat_history_clone.append({"role":"assistant","content":"Summarize the provided chat history"})
    url = "https://openai.ru9.workers.dev/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
    }
    data = {'model': 'gpt-4-1106-preview', 'messages': chat_history_clone, 'temperature':0.5}
    response = requests.post(url, headers=headers, json=data)
    assistant_reply = response.json()['choices'][0]['message']['content']
    return assistant_reply
