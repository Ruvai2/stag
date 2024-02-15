Steps to run a tool agent:
# OpenAi Chat model for interacting with open-interpreter/self-operating computer
    
## Installation

### Step 1: Clone and setup the Repository

```bash
git clone https://github.com/Ruvai2/Daasi.git
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
## Usage

Follow these steps to run the project:

```bash
# Navigate to the project directory
cd Daasi/

# Run the main.py file
uvicorn main:app --reload

# Hit your http request on below endpoint:
`127.0.0.1:8000/api/openai`
e.g: {"key": "Open youtube for me"}

# Make sure open-interpreter-tool/self-operating-computer is running in background
```
## License

This project is licensed under the [MIT License](LICENSE).

#### note: update interpreter.llm.api_key in `main.py`

## Docker setup for developement
#### go inside the project dir
#### build and start docker container
### `docker-compose up` 
#### access the docker container
### `docker exec -ti interpreter-server bash`
####  docker container stop
### `docker-compose stop`
#### re-build docker image
### `docker-compose up --build`
### URL
### `http://localhost:8000`