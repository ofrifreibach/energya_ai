from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

load_dotenv(override=True)

from chatbot import ask_energy_consultant


BASE_DIR = Path(__file__).resolve().parent

MAX_HISTORY_MESSAGES = 20
MAX_HISTORY_CHARACTERS = 8000

limiter = Limiter(key_func=get_remote_address)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(
        min_length=1,
        max_length=2000,
    )


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=500,
    )
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=MAX_HISTORY_MESSAGES,
    )


app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.post("/api/chat")
@limiter.limit("10/minute")
def chat(request: Request, chat_request: ChatRequest):
    history = [
        message.model_dump()
        for message in chat_request.history
    ]

    total_history_characters = sum(
        len(message["content"])
        for message in history
    )

    if total_history_characters > MAX_HISTORY_CHARACTERS:
        history = history[-6:]

    answer = ask_energy_consultant(
        question=chat_request.question,
        history=history,
    )

    return {"answer": answer}