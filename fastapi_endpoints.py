# Run with command: ```fastapi dev fastapi_endpoints.py``` (auto-reload enabled)
# OR ```fastaspi run fastapi_endpoints.py``` (auto-reload disabled)
from fastapi import FastAPI
from pydantic import BaseModel
from .backend_agent import AgentWithChatGPT

class UserMessage(BaseModel):
    '''
    User message with configuration, the `thread_id` is to identify the user, 
    so that the model can manage history of the conversation for each user/session.
    Example:
        {
            "message": "Hello",
            "config": {"configurable": {"thread_id": "user1234"}
        }
    '''
    message: str
    config: dict

    def dict(self):
        return {"message": self.message, "config": self.config}

app = FastAPI()
app.agent = AgentWithChatGPT()

@app.get("/")
async def read_root():
    return "Navigate to /docs to see the API documentation."

@app.post("/chat")
async def get_model_response(user_message: UserMessage):
    model_response = app.agent.answer_with_session_config(user_message.dict())
    return {"response": model_response}