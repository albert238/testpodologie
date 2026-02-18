from __future__ import annotations

import csv
import io
import json
import secrets
from typing import Any, Dict, List

from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session as OrmSession

from db import engine, Base, get_db
import models
import seed

app = FastAPI(title="Podologie • Formation vendeurs")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def _startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse(
        "landing.html",
        {"request": request, "byline": "BY Clara Vialle"},
    )


@app.get("/init")
def init(db: OrmSession = Depends(get_db)):
    token = seed.upsert_seed(db=db)
    return RedirectResponse(url=f"/t/{token}", status_code=302)


@app.post("/start")
def start(db: OrmSession = Depends(get_db)):
    token = seed.upsert_seed(db=db)
    return RedirectResponse(url=f"/t/{token}", status_code=302)


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, db: OrmSession = Depends(get_db)):
    sessions = db.query(models.Session).order_by(models.Session.id.desc()).limit(200).all()
    return templates.TemplateResponse("admin.html", {"request": request, "sessions": sessions})


@app.get("/admin/export.csv")
def export_csv(db: OrmSession = Depends(get_db)):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["created_at", "token", "consent", "role", "experience", "shop_type"])

    sessions = db.query(models.Session).order_by(models.Session.id.desc()).all()
    for s in sessions:
        w.writerow([s.created_at, s.token, int(s.consent), s.role, s.experience, s.shop_type])

    out.seek(0)
    return StreamingResponse(
        iter([out.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=podotest_sessions.csv"},
    )


@app.get("/t/{token}", response_class=HTMLResponse)
def take_quiz(token: str, request: Request, db: OrmSession = Depends(get_db)):
    sess = db.query(models.Session).filter(models.Session.token == token).first()
    if not sess:
        return templates.TemplateResponse("done.html", {"request": request, "message": "Lien invalide."}, status_code=404)

    quiz = db.query(models.Quiz).filter(models.Quiz.id == sess.quiz_id).first()
    if not quiz:
        return templates.TemplateResponse("done.html", {"request": request, "message": "Quiz introuvable."}, status_code=404)

    questions = (
        db.query(models.Question)
        .filter(models.Question.quiz_id == quiz.id)
        .order_by(models.Question.id.asc())
        .all()
    )

    q_payload: List[Dict[str, Any]] = []
    for q in questions:
        try:
            choices = json.loads(q.choices_json or "[]")
        except Exception:
            choices = []
        q_payload.append(
            {
                "id": q.id,
                "kind": q.kind,
                "topic": q.topic,
                "text": q.text,
                "choices": choices,
            }
        )

    return templates.TemplateResponse(
        "quiz.html",
        {"request": request, "quiz_title": quiz.title, "token": token, "questions": q_payload},
    )


@app.post("/t/{token}", response_class=HTMLResponse)
async def submit_quiz(token: str, request: Request, db: OrmSession = Depends(get_db)):
    sess = db.query(models.Session).filter(models.Session.token == token).first()
    if not sess:
        return templates.TemplateResponse("done.html", {"request": request, "message": "Lien invalide."}, status_code=404)

    form = await request.form()

    # récup questions
    questions = (
        db.query(models.Question)
        .filter(models.Question.quiz_id == sess.quiz_id)
        .order_by(models.Question.id.asc())
        .all()
    )

    # enregistre réponses + calc correct
    for q in questions:
        key = f"q{q.id}"

        if q.kind == "multi":
            selected_ids = sorted([str(x) for x in form.getlist(key)])
        else:
            v = form.get(key, "")
            selected_ids = [str(v)] if v else []

        try:
            choices = json.loads(q.choices_json or "[]")
        except Exception:
            choices = []
        correct_ids = sorted([c.get("id") for c in choices if c.get("is_correct")])

        is_correct = (selected_ids == correct_ids)

        existing = (
            db.query(models.Answer)
            .filter(models.Answer.session_id == sess.id, models.Answer.question_id == q.id)
            .first()
        )
        if existing:
            existing.selected_json = json.dumps(selected_ids, ensure_ascii=False)
            existing.is_correct = is_correct
        else:
            db.add(
                models.Answer(
                    session_id=sess.id,
                    question_id=q.id,
                    selected_json=json.dumps(selected_ids, ensure_ascii=False),
                    is_correct=is_correct,
                )
            )

    db.commit()
    return templates.TemplateResponse("done.html", {"request": request, "message": "Merci ! Réponses enregistrées ✅"})
