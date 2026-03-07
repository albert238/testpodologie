from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from db import Base

class Quiz(Base):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, default="Test Podologie")
    slug: Mapped[str] = mapped_column(String, default="demo", unique=True, index=True)
    author: Mapped[str] = mapped_column(String, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    questions: Mapped[list["Question"]] = relationship(back_populates="quiz", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    kind: Mapped[str] = mapped_column(String)  # "single" | "multi"
    text: Mapped[str] = mapped_column(Text)
    choices_json: Mapped[str] = mapped_column(Text)  # JSON string of choices [{id,label,is_correct,feedback?}]
    topic: Mapped[str] = mapped_column(String, default="general")  # pour stats par thème

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")

class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Profil candidat
    prenom: Mapped[str] = mapped_column(String, default="")
    nom: Mapped[str] = mapped_column(String, default="")
    consent: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String, default="")
    experience: Mapped[str] = mapped_column(String, default="")
    shop_type: Mapped[str] = mapped_column(String, default="")
    # IDs des questions tirées aléatoirement pour cette session (JSON)
    question_ids_json: Mapped[str] = mapped_column(Text, default="[]")

    answers: Mapped[list["Answer"]] = relationship(cascade="all, delete-orphan")

class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    selected_json: Mapped[str] = mapped_column(Text)  # JSON string: ["A","C"]
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
