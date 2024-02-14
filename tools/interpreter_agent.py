from utils.request import request_handler
URL = 'http://127.0.0.1:8000/'
SELF_OPERATING_URL = 'http://127.0.0.1:1081/'

# This method is used to connect with open-interpreter
def interpreter_tool(query):
    try:
        print("::::::query::::::::::", query)
        request_handler(URL+'api/openai', {'key':query})
    except Exception as e:
        print(":::interpreter_tool::: ERROR::",e)


def self_operating_computer(query, summary):
    """
    A function that operates a computer on its own. It takes a query and a summary, makes a request to a self-operating system API, and returns the response. If an exception occurs, it prints an error message.
    """
    try:
        print('Inside self_operatig_computer:::', query)
        return request_handler(SELF_OPERATING_URL+'api/self-operating-system', {'query':query, 'summary':False})

    except Exception as e:
        print(":::self_operating_computer::: ERROR::",e) 

def gpt_agent(query):
    """
    A function that connects with the OpenAI chat API. It takes a query as input and returns the response from the OpenAI chat API. If an exception occurs, it prints an error message.
    """
    try:
        print('Inside gpt_main:::', query)
        return request_handler(URL+'api/gpt', {'key':query})
    except Exception as e:
        print(":::gpt_main::: ERROR::",e)       