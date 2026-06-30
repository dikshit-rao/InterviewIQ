import os
import json
from typing import List

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import UPLOAD_DIR
from database import init_db, get_db, Document, Interview, Answer
from models import (
    QuestionRequest, AnswerResponse, Citation,
    StartInterviewRequest, AnswerSubmit, EvaluateRequest, Evaluation,
)
from pipeline import build_vector_database
from retriever import retrieve_chunks
from llm import generate_answer, generate_question, evaluate_answer

app = FastAPI(title="InterviewIQ")

# Without CORS, EVERY request from your frontend will fail in the browser.
# Lock allow_origins down to your real frontend URL before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup if they don't exist
init_db()


@app.get("/")
def home():
    return {"message": "InterviewIQ Backend Running"}


# ---------------- Documents ----------------
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    name = file.filename.replace(".pdf", "")

    # Guard: if this document is already indexed, do NOT index it again
    # (re-indexing appends duplicate vectors and pollutes retrieval).
    existing = db.query(Document).filter(Document.name == name).first()
    if existing:
        return {
            "message": f"{name} is already uploaded. Delete it first to re-index.",
            "document_name": name,
            "total_chunks": existing.total_chunks,
            "already_exists": True,
        }

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    total_chunks = build_vector_database(file_path)

    db.add(Document(name=name, total_chunks=total_chunks))
    db.commit()

    return {
        "message": f"{file.filename} uploaded successfully",
        "document_name": name,
        "total_chunks": total_chunks,
        "already_exists": False,
    }


@app.post("/upload-multiple")
async def upload_multiple(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Upload several PDFs at once. Each is indexed into the same global
    store, so you can then search across any of them via /ask."""
    results = []
    for file in files:
        name = file.filename.replace(".pdf", "")

        existing = db.query(Document).filter(Document.name == name).first()
        if existing:
            results.append({
                "document_name": name,
                "status": "already_exists",
                "total_chunks": existing.total_chunks,
            })
            continue

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        total_chunks = build_vector_database(file_path)
        db.add(Document(name=name, total_chunks=total_chunks))
        db.commit()

        results.append({
            "document_name": name,
            "status": "uploaded",
            "total_chunks": total_chunks,
        })

    return {"results": results}


@app.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    return [{"name": d.name, "total_chunks": d.total_chunks} for d in docs]


# ---------------- AI Chat (RAG + citations) ----------------
@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    chunks = retrieve_chunks(request.question, request.documents)
    answer = generate_answer(request.question, chunks)

    # Build de-duplicated citations (source + page)
    seen, citations = set(), []
    for c in chunks:
        key = (c["source"], c["page"])
        if key not in seen:
            seen.add(key)
            citations.append(Citation(source=c["source"], page=c["page"]))

    return AnswerResponse(
        question=request.question, answer=answer, citations=citations
    )


# ---------------- Mock Interview (session flow) ----------------
@app.post("/interview/start")
def interview_start(request: StartInterviewRequest, db: Session = Depends(get_db)):
    """Create an interview session and return the first question."""
    interview = Interview(
        subject=request.subject,
        difficulty=request.difficulty,
        score=0.0,
        total_questions=0,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    question = generate_question(request.subject, request.difficulty)
    return {
        "interview_id": interview.id,
        "subject": interview.subject,
        "difficulty": interview.difficulty,
        "question": question,
    }


@app.post("/interview/answer")
def interview_answer(request: AnswerSubmit, db: Session = Depends(get_db)):
    """Evaluate one answer, save it, update the running score, return the
    evaluation plus the next question."""
    interview = db.query(Interview).filter(Interview.id == request.interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # 1. Evaluate the answer with the LLM
    data = evaluate_answer(interview.subject, request.question, request.user_answer)

    # 2. Save the answer
    db.add(Answer(
        interview_id=interview.id,
        question=request.question,
        user_answer=request.user_answer,
        score=data["score"],
        feedback=json.dumps(data),
    ))
    db.commit()

    # 3. Recompute running aggregates for this interview
    answers = db.query(Answer).filter(Answer.interview_id == interview.id).all()
    interview.total_questions = len(answers)
    interview.score = round(sum(a.score for a in answers) / len(answers), 2)
    db.commit()

    # 4. Next question, avoiding ones already asked this session
    asked = [a.question for a in answers]
    next_question = generate_question(interview.subject, interview.difficulty, asked=asked)

    return {
        "evaluation": data,
        "running_score": interview.score,
        "questions_answered": interview.total_questions,
        "next_question": next_question,
    }


@app.get("/interview/{interview_id}")
def interview_detail(interview_id: int, db: Session = Depends(get_db)):
    """Full transcript of one interview."""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    answers = db.query(Answer).filter(Answer.interview_id == interview_id).all()
    return {
        "interview_id": interview.id,
        "subject": interview.subject,
        "difficulty": interview.difficulty,
        "score": interview.score,
        "total_questions": interview.total_questions,
        "answers": [
            {"question": a.question, "user_answer": a.user_answer, "score": a.score}
            for a in answers
        ],
    }


# ---------------- Dashboard ----------------
@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    doc_count = db.query(Document).count()
    # only count interviews where at least one question was answered
    interviews = db.query(Interview).filter(Interview.total_questions > 0).all()
    taken = len(interviews)
    avg = round(sum(i.score for i in interviews) / taken, 1) if taken else 0.0

    # per-subject averages -> strong / weak areas
    subj_scores = {}
    for i in interviews:
        subj_scores.setdefault(i.subject, []).append(i.score)
    subj_avg = {s: round(sum(v) / len(v), 1) for s, v in subj_scores.items()}

    strong = [s for s, sc in subj_avg.items() if sc >= 7]
    weak = [s for s, sc in subj_avg.items() if sc < 5]

    return {
        "uploaded_documents": doc_count,
        "interviews_taken": taken,
        "average_score": avg,
        "strong_areas": strong,
        "weak_areas": weak,
    }


# ---------------- Performance ----------------
@app.get("/performance")
def performance(db: Session = Depends(get_db)):
    """Per-subject performance for the Performance module."""
    interviews = db.query(Interview).filter(Interview.total_questions > 0).all()
    subj = {}
    for i in interviews:
        subj.setdefault(i.subject, {"scores": [], "questions": 0})
        subj[i.subject]["scores"].append(i.score)
        subj[i.subject]["questions"] += i.total_questions

    return [
        {
            "subject": s,
            "average_score": round(sum(d["scores"]) / len(d["scores"]), 2),
            "interviews": len(d["scores"]),
            "questions_attempted": d["questions"],
        }
        for s, d in subj.items()
    ]