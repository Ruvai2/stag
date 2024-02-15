from  utils.request_handler import request_handler
URL = 'http://127.0.0.1:8000/'


# This method is used to connect with open-interpreter
def interpreter_tool(query):
    try:
        print("::::::query::::::::::", query)
        request_handler(URL+'api/openai', {'key':query})
    except Exception as e:
        print(":::interpreter_tool::: ERROR::",e)