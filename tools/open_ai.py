# import requests
# chat_history = []
# def open_ai_main(content):
#     try:
#         chat_history.append({"role":"user","content":content})
#         url = "https://openai.ru9.workers.dev/v1/chat/completions"
#         headers = {
#             "Content-Type": "application/json",
#         }
#         data = {'model': 'gpt-4-1106-preview', 'messages': chat_history}
#         response = requests.post(url, headers=headers, json=data)
#         assistant_reply = response.json()['choices'][0]['message']['content']
#         chat_history.append({"role": "assistant", "content": assistant_reply})
#         return {'result': response.json()['choices'][0]['message']['content']}
#     except Exception as e:
#         print(":::open_ai_main::: ERROR::",e)
#         return {'result': 'Error'}
