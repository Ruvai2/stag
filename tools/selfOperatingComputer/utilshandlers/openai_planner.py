# purpose and summary of this code
#----------------------------------------------------------
# This code is a simple chat client for interacting with the OpenAI API. It maintains a chat history and sends user messages to the OpenAI API, then receives and stores the assistant's responses. The createChatClient function is the main function that handles the interaction with the OpenAI API. The ai_planner_1, ai_planner_2, and ai_planner_3 functions are used to interact with the OpenAI API and get responses from three different AI planners. The ai_solution_marking function is used to mark the solutions from the planners and return the result. The chat_history list is used to store the chat history, and the chat_history_planner1, chat_history_planner2, and chat_history_planner3 lists are used to store the chat history for each planner. The ai_solution_marking_point list is used to store the marked solutions from the planners. The purpose of this code is to provide a simple interface for interacting with the OpenAI API and processing the responses from the AI planners. The main function createChatClient handles the interaction with the OpenAI API and stores the chat history, while the other functions are used to interact with the OpenAI API and process the responses from the AI planners. The code is designed to be modular and easy to understand, making it suitable for integration into a larger system.

import requests
from operate.operate import thought_history

thought_history.append({
        "role": "system",
        "content": "You are a AI orchestrator, You will answer the last asked question by user from the user and assistant history in summarised form."
      })

def summarize_chat_history(content):
    thought_history.append({"role":"user","content":content})
    print('chat_history:',thought_history)
    url = "https://openai.ru9.workers.dev/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
    }
    data = {'model': 'gpt-4-1106-preview', 'messages': thought_history, 'temperature':0.5}
    response = requests.post(url, headers=headers, json=data)
    assistant_reply = response.json()['choices'][0]['message']['content']
    return assistant_reply
