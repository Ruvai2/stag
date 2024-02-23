from  utils.request_handler import request_handler
BASE_URL = 'http://127.0.0.1:'


# This method is used to connect with open-interpreter
def interpreter_tool(query,summary,portId):
    try:
        print("::::::query::::::::::", query, "::::::summary::::::::::", summary)
        request_handler(BASE_URL+portId+'/api/openai', {'key':query, 'summary':summary})
    except Exception as e:
        print(":::interpreter_tool::: ERROR::",e)