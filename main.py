from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv(override=True)

from chatbot import ask_energy_consultant


BASE_DIR = Path(__file__).resolve().parent


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[ChatMessage] = Field(default_factory=list)


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

    answer = ask_energy_consultant(
        question=request.question,
        history=history,
    )

    return {"answer": answer}