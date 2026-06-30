"""SQLite + SQLAlchemy.

This is the piece your Dashboard and Performance modules need.
'Interviews Taken: 26', 'Average Score: 8.3', per-subject scores — all of
that is relational data that has to live in a real table, not a JSON file.
"""
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

from config import DB_PATH

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},  # needed for SQLite + FastAPI
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    total_chunks = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class Interview(Base):
    __tablename__ = "interviews"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    difficulty = Column(String)
    score = Column(Float, default=0.0)            # average over the interview
    total_questions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, index=True)
    question = Column(Text)
    user_answer = Column(Text)
    score = Column(Float)
    feedback = Column(Text)


def init_db():
    """Create all tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency — yields a session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()