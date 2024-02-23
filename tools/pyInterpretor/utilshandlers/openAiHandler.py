import requests

chat_history = []
chat_history.append({
        "role": "system",
        "content": "You are a AI orchestrator, When you get a requst you will 1. Understand the request and query back to with a plan and what i need to run. And you need to tell me step by step how to do it. "
      })
chat_history.append({
        "role": "user",
        "content": "Hi, Open Interpretor, Sure "
  })
chat_history.append(  {
        "role": "assistant",
        "content": "Hello!"
      }
)
def createChatClient(content):

  chat_history.append({"role":"user","content":content})

  url = "https://openai.ru9.workers.dev/v1/chat/completions"
  headers = {
      "Content-Type": "application/json",
      # "Authorization": "Bearer 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"
  }
  data = {'model': 'gpt-4-1106-preview', 'messages': chat_history}
  response = requests.post(url, headers=headers, json=data)
  assistant_reply = response.json()['choices'][0]['message']['content']
  chat_history.append({"role": "system", "content": assistant_reply})
  # print(":::::::chat_history:::::::::::", chat_history)
  return {'result': response.json()['choices'][0]['message']['content']}

