from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

load_dotenv(override=True)

from chatbot import ask_energy_consultant


class ChatRequest(BaseModel):
    question: str


app = FastAPI()


@app.get("/")
def home():
    return FileResponse("index.html")


@app.post("/api/chat")
def chat(request: ChatRequest):
    answer = ask_energy_consultant(request.question)
    return {"answer": answer}