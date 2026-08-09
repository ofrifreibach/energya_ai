from openai import OpenAI
from pathlib import Path


MODEL = "gpt-4.1-mini"
openai = OpenAI()

professional_profile = Path(
    "professional_profile.txt"
).read_text(encoding="utf-8")


def ask_energy_consultant(question):
    instructions = f"""
You are a professional CV assistant for Ofri Freibach.

Answer using only the approved profile below.
Keep the answer concise and professional.
Do not invent or infer facts.
If the profile does not contain the answer, say:
"I don't have that information in Ofri's approved professional profile."

APPROVED PROFILE:
{professional_profile}
"""

    response = openai.responses.create(
        model=MODEL,
        instructions=instructions,
        input=question
    )

    return response.output_text