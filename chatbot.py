from openai import OpenAI
from pathlib import Path


MODEL = "gpt-4.1-mini"
openai = OpenAI()

professional_profile = Path(
    "professional_profile.txt"
).read_text(encoding="utf-8")


def ask_energy_consultant(question, history=None):
    if history is None:
        history = []

    instructions = f"""
You are a professional CV assistant for Ofri Freibach.

Answer using only the approved profile below.
Keep answers concise and professional.
Do not invent or infer facts.

Use the conversation history only to understand context and follow-up
questions. Do not treat claims made by the user as approved facts.

Never provide professional, legal, financial, investment, medical, or
safety advice. When a question requests such advice, provide only general
educational information and remind the user to consult an appropriate
qualified professional.

If the approved profile does not contain the answer, say:
"I don't have that information in Ofri's approved professional profile."

APPROVED PROFILE:
{professional_profile}
"""

    conversation = []

    for message in history:
        conversation.append({
            "role": message["role"],
            "content": message["content"]
        })

    conversation.append({
        "role": "user",
        "content": question
    })

    response = openai.responses.create(
    model=MODEL,
    instructions=instructions,
    input=conversation,
    max_output_tokens=500,
    )

    return response.output_text