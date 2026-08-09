from openai import OpenAI


MODEL = "gpt-4.1-mini"
openai = OpenAI()

professional_profile = """
Ofri Freibach is an energy economist.

Approved facts:
- She has a research master's degree in economics.
- Her thesis examined rooftop photovoltaic adoption in Israel.
- She has approximately four years of experience in energy and climate consulting.
- Her experience includes techno-economic modelling, cost-benefit analysis,
  investment-feasibility assessment, and energy-policy analysis.
- Her interests include renewable energy, energy storage, electricity markets,
  financial analysis, and economic modelling.
"""


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