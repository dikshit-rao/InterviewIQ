import json

import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL
from prompts import RAG_PROMPT, INTERVIEW_QUESTION_PROMPT, EVALUATION_PROMPT

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)


def _safe_text(response):
    """Gemini can return a blocked/empty response that has no `.text`.
    Accessing .text in that case raises — so we guard it."""
    try:
        return response.text
    except Exception:
        return ""


def generate_answer(question, retrieved_chunks):
    context = "\n\n".join(c["text"] for c in retrieved_chunks)
    prompt = RAG_PROMPT.format(context=context, question=question)
    text = _safe_text(model.generate_content(prompt))
    return text or "I could not generate an answer. Please try again."


def generate_question(subject, difficulty, asked=None):
    asked_str = "\n".join(asked) if asked else "None"
    prompt = INTERVIEW_QUESTION_PROMPT.format(
        subject=subject, difficulty=difficulty, asked=asked_str
    )
    return _safe_text(model.generate_content(prompt)).strip()


def evaluate_answer(subject, question, user_answer):
    """Returns a dict matching the Evaluation schema. Forces JSON output."""
    prompt = EVALUATION_PROMPT.format(
        subject=subject, question=question, user_answer=user_answer
    )
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"},
    )
    raw = _safe_text(response)
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        # Fallback so the frontend never crashes on a bad parse
        return {
            "score": 0,
            "correct_points": [],
            "missing_points": ["Could not parse the evaluation. Please retry."],
            "model_answer": "",
        }