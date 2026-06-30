from typing import List

from pydantic import BaseModel


class Student(BaseModel):
    name: str
    college: str


# ---------- RAG Chat ----------
class QuestionRequest(BaseModel):
    question: str
    documents: List[str] = []   # multi-select; empty list = search ALL documents


class Citation(BaseModel):
    source: str
    page: int


class AnswerResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation]


# ---------- Mock Interview ----------
class StartInterviewRequest(BaseModel):
    subject: str
    difficulty: str


class AnswerSubmit(BaseModel):
    interview_id: int
    question: str
    user_answer: str


class EvaluateRequest(BaseModel):
    subject: str
    question: str
    user_answer: str


class Evaluation(BaseModel):
    score: float
    correct_points: List[str]
    missing_points: List[str]
    model_answer: str