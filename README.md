# Energy Economics AI Consultant

A web-based AI assistant built by Ofri Freibach.

The current version answers questions about my professional background using an approved knowledge source derived from my CV. It is instructed to provide concise, grounded answers and avoid inventing qualifications or experience.

## Current Features

- Web-based question-and-answer interface
- Answers grounded in an approved professional profile
- Fallback response when the requested information is unavailable
- FastAPI backend
- OpenAI Responses API integration

## Project Structure

- `main.py` – FastAPI server and API endpoint
- `chatbot.py` – AI instructions and response logic
- `professional_profile.txt` – approved professional information
- `index.html` – browser interface
- `cv_chat.ipynb` – initial experiments

## Technologies

- Python
- FastAPI
- OpenAI API
- HTML and JavaScript

## Author

Ofri Freibach  
Energy economist specializing in renewable energy, energy storage, economic modelling, and energy-policy analysis.