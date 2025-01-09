# chat-agent-langchain

## Introduction
An agent with an OpenAI LLM model as the core.

Functionalities:
- Extract knowledge from PDF to answer questions (replace Customer Service human)
- Answer general questions that does not require knowledge.
- Has built-in memory to record details of the conversation, for each user indepedently.

## Installation
### Prerequisites
Make sure you subscribed to OpenAI API and have your API key. Create a file named 'api_key.py' file with `OPENAI_API_KEY` variable:
```python filename="api_key.py"
OPENAI_API_KEY = 'your-api-key
```
### Installation
First, install all requried dependencies with
```bash
pip install -r requirements.txt
```
Start the API Service with
```bash
fastapi run fastapi_endpoints.py
```
Now, the service is online (in your localhost) and you can view the API document by browse `127.0.0.1:8000/docs` in your browser.
## Send request to server
Once the API server is online,

1. In bash terminal, send curl request:
    ```
    curl --header "Content-Type: application/json" \
    --request POST \
    --data '{"message":"Hello, my name is Kelvin", "config": {"configurable": {"thread_id": "user001"}}}' \
    http://localhost:8000/chat
    ```
    Response from the API:
    > {"response":"Hello Kelvin! How can I assist you today?"}

2. Check out if the model remember your name by requesting again with the same `thread_id`

    ```
    curl --header "Content-Type: application/json" \
    --request POST \
    --data '{"message":"What is my name?", "config": {"configurable": {"thread_id": "user001"}}}' \
    http://localhost:8000/chat
    ```
    Response from the API:
    > {"response":"Your name is Kelvin."}