import sqlite3
from datetime import datetime, timezone
from uuid import uuid4
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
DATABASE_PATH = BASE_DIR / "conversations.db"

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
    session_id: str | None = Field(
    default=None,
    max_length=100,
    )

def initialize_database():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL
            )
            """
        )


def save_conversation(session_id: str, question: str, answer: str):
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO conversations (
                session_id,
                created_at,
                question,
                answer
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                session_id,
                datetime.now(timezone.utc).isoformat(),
                question,
                answer,
            ),
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

@app.on_event("startup")
def startup_event():
    initialize_database()

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

    session_id = chat_request.session_id or str(uuid4())

    save_conversation(
        session_id=session_id,
        question=chat_request.question,
        answer=answer,
    )

    return {
        "answer": answer,
        "session_id": session_id,
    }