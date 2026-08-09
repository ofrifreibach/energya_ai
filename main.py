from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv(override=True)

from chatbot import ask_energy_consultant


BASE_DIR = Path(__file__).resolve().parent

MAX_HISTORY_MESSAGES = 10
MAX_HISTORY_CHARACTERS = 8000


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=MAX_HISTORY_MESSAGES,
    )


app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.post("/api/chat")
def chat(request: ChatRequest):
    history = [
        message.model_dump()
        for message in request.history
    ]

    total_history_characters = sum(
        len(message["content"])
        for message in history
    )

    if total_history_characters > MAX_HISTORY_CHARACTERS:
        history = history[-6:]

    answer = ask_energy_consultant(
        question=request.question,
        history=history,
    )

    return {"answer": answer}