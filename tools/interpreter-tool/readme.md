# Open Interpreter

## Installation

### Step 1: Clone the Repository and folow readme to start this repo server

```bash
git clone https://github.com/Ruvai2/Daasi/tree/INP-5-create-proxy-ai-modifiation
```

### Step 2: Installation Setup for macOS

1. Install Python 3 using Homebrew:

    ```bash
    brew install python@3.11
    ```

2. Install PIP and upgrade to version 23.3.2:

    ```bash
    python3 -m pip install --upgrade pip==23.3.2
    ```

### Step 3: Clone the official repo of open-interpreter
 ```bash
git clone https://github.com/KillianLucas/open-interpreter
 ```
### Step 4: Follow the steps to setup your interpreter-tools 
1. clone this repo into your system:
    ```bash
    https://github.com/w3villa/ruv-interpreter-tool-agent.git
    ```
2. copy the path of open-interpreter repo (mentioned in step 3) and paste it in .env of above cloned repo
    ```bash
    OPEN_INTERPRETER_PATH = 'ENTER YOUR OPEN INTERPRETER PATH HERE'
    ```

## Usage
Follow these steps to run the project:
```bash
# Navigate to the project directory
cd /ruv-interpreter-tool-agent

# Run the main.py file
uvicorn main:app --reload --port 9000

# send you http request on http://127.0.0.1:8000/api/openai
{
    "key":"open youtube for me"
}
```

## License

This project is licensed under the [MIT License](LICENSE).