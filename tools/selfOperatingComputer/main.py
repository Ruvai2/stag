# Import the sys module which provides access to some variables used or maintained by the Python interpreter and to functions that interact strongly with the interpreter.
import sys

# Append the path '/home2/AITaskManager/self-operating-computer' to the system path. This is done to include this directory in the list of paths that Python will search in for files when importing modules.
sys.path.append('/Users/abhishekanand/Documents/self-operating-computer')

# Import the FastAPI framework. FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
import fastapi as _fastapi

# Import the BaseModel from pydantic. BaseModel is the main class to inherit from in Pydantic. It provides the main functionality for data validation and settings management.
from pydantic import BaseModel

# Import the main function from the operate module located in the operate directory.
from operate.operate import main, thought_history

from utilshandlers.openai_planner import summarize_chat_history

# Create an instance of the FastAPI class. This instance is the main application.
app = _fastapi.FastAPI()

# Define a Pydantic model named Item. This model has a single field 'key' of type str. Pydantic models are used for data validation, serialization and documentation.
class Item(BaseModel):
    key: str
    summary: bool = False

# Define a route for the FastAPI application. This route is a POST route at the path "/operate". The function associated with this route is called 'operate'.
@app.post("/operate")
def operate(message: Item):
    # The function 'operate' takes a single parameter 'message' of type Item. This parameter is automatically validated by FastAPI using the Pydantic model.

    # The function 'operate' tries to execute the 'main' function from the 'operate' module with the parameters "gpt-4-with-ocr", the 'key' field of the 'message' parameter and False.
    try:
        if not message.summary:
            thought_history.append({"role":"user","content":message.key})
            main('gpt-4', message.key, False)
        else:
            print("::::::::Summarizing chat history::::::")
            summary = summarize_chat_history(message.key)
            print("::::::::Summary::::::", summary)
            return {"result": summary}
    except Exception as e:
        return {"message": str(e)}
    

    # Summary:
    # The provided Python code defines a FastAPI application with a single POST endpoint at "/operate". The endpoint accepts a JSON body with a single field 'key' of type string, validated by the Pydantic model Item.

    # When a request is made to this endpoint, the operate function is invoked. It attempts to execute the main function from the operate module with parameters "gpt-4-with-ocr", the 'key' from the request, and False.

    # If the main function executes successfully, a JSON response with a message "success" is returned. If an exception occurs, the exception message is returned in the JSON response.