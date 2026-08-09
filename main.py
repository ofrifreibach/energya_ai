from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

load_dotenv(override=True)

from chatbot import ask_energy_consultant


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[ChatMessage] = []


app = FastAPI()
app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/")
def home():
    return FileResponse("index.html")


@app.post("/api/chat")
def chat(request: ChatRequest):
    history = [
        message.model_dump()
        for message in request.history
    ]

    answer = ask_energy_consultant(
        question=request.question,
        history=history
    )

    return {"answer": answer}