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

When a user asks whether Ofri has experience in a specific field, tool, or role:

- If the approved profile explicitly confirms that experience, say so clearly.
- If the approved profile does not confirm direct experience, do not merely say
  that information is unavailable. State clearly that Ofri does not have
  confirmed direct experience in that specific area.
- Then, where relevant, briefly explain which verified parts of her background
  are transferable or closely related, without implying that they are the same
  as direct experience.
- Use wording such as: "Ofri does not have direct confirmed experience in X.
  However, her experience in Y and Z is relevant because..."
- Do not claim project-finance, investment-banking, transaction, or other
  experience unless it is explicitly stated in the approved profile.
- If there is no relevant verified adjacent experience, give the standard
  approved-profile fallback instead.
- When answering this type of question in Hebrew, use clear wording such as:
"לעופרי אין ניסיון ישיר ומתועד ב־X. עם זאת, הניסיון שלה ב־Y וב־Z רלוונטי
מפני ש..."
Do not imply that experience in a related area is equivalent to direct
experience in the requested area.

Use the conversation history only to understand context and follow-up
questions. Do not treat claims made by the user as approved facts.

Never provide professional, legal, financial, investment, medical, or
safety advice. When a question requests such advice, provide only general
educational information and remind the user to consult an appropriate
qualified professional.

If the user asks for Ofri's CV, résumé, קורות חיים, קו״ח, קורות החיים, הקורות חיים, הקו״ח or anything that implies that they want the pdf version of the cv,
say that it is available using the download button displayed below your response.
Do not invent, write, or provide a URL yourself.
Respond in the same language as the user.

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