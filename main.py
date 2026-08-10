import html
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
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
admin_security = HTTPBasic()


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

def get_conversations():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        return connection.execute(
            """
            SELECT session_id, created_at, question, answer
            FROM conversations
            ORDER BY id DESC
            LIMIT 200
            """
        ).fetchall()


def verify_admin(
    credentials: HTTPBasicCredentials = Depends(admin_security),
):
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_username or not admin_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin access is not configured.",
        )

    username_is_correct = secrets.compare_digest(
        credentials.username,
        admin_username,
    )
    password_is_correct = secrets.compare_digest(
        credentials.password,
        admin_password,
    )

    if not username_is_correct or not password_is_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Basic"},
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

@app.get("/admin", response_class=HTMLResponse)
def admin_page(
    credentials: HTTPBasicCredentials = Depends(verify_admin),
):
    conversations = get_conversations()

    rows = ""

    for conversation in conversations:
        rows += f"""
        <tr>
            <td>{html.escape(conversation["created_at"])}</td>
            <td>{html.escape(conversation["session_id"][:8])}</td>
            <td>{html.escape(conversation["question"])}</td>
            <td>{html.escape(conversation["answer"])}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat Conversations</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
                background: #f5f7f9;
                color: #1f2933;
            }}

            h1 {{
                margin-bottom: 8px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}

            th, td {{
                padding: 12px;
                border: 1px solid #d9e2ec;
                text-align: left;
                vertical-align: top;
                white-space: pre-wrap;
            }}

            th {{
                background: #243b53;
                color: white;
            }}

            tr:nth-child(even) {{
                background: #f0f4f8;
            }}
        </style>
    </head>
    <body>
        <h1>Chat conversations</h1>
        <p>Showing the 200 most recent messages.</p>

        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Session</th>
                    <th>Question</th>
                    <th>Answer</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </body>
    </html>
    """

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