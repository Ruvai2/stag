import requests

conversaion_history = []
CHAT_COMPLETEION_URL = "https://openai.ru9.workers.dev/v1/chat/completions"
def planner_method(content):
#   conversaion_history = chat_history[:]
  conversaion_history.append({"role":"user","content": "Human is asking for a question like this can you answer the question by understanding the past responses:" + content })

  url = CHAT_COMPLETEION_URL
  headers = {
      "Content-Type": "application/json",
  }
  data = {'model': 'gpt-4-1106-preview', 'messages': conversaion_history, 'temperature':0.2}
  response = requests.post(CHAT_COMPLETEION_URL, headers=headers, json=data)
  assistant_reply = response.json()['choices'][0]['message']['content']
  conversaion_history.append({"role": "system", "content": assistant_reply})
  return {'result': response.json()['choices'][0]['message']['content']}