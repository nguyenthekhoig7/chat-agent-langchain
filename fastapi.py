from fastapi import FastAPI

app = FastAPI()


@app.post("/chat")
async def root():
    return {"message": "Hello World"}