import sys
sys.path.append('/Users/abhishekanand/Documents/self-operating-computer')
from fastapi import FastAPI
app = FastAPI()
from operate.operate import main, thought_history
from template.protocol import SelfComputerRequest
from utils.request_handler import request_handler
from utils.ai_planner import ai_planner, summarize_chat_history

@app.post("/api/self-operating-system")
def root(args: SelfComputerRequest):
    try:
        if not args.summary:
            thought_history.append({"role":"user","content":args.query})
            main('gpt-4', args.query, False)
        else:
            print("Summarizing chat history")
            summary = summarize_chat_history(args.query)
            return {"summary": summary}
    except Exception as e:
        print(e)