from __future__ import annotations

import csv
import io
import json
import secrets
from typing import Any, Dict, List

from fastapi import FastAPI, Request, Depends, Cookie
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

# ── Mot de passe admin ─────────────────────────────────────────────────────────
ADMIN_PASSWORD = "admin"
# Sessions admin actives (en mémoire — suffisant pour cet usage)
_admin_sessions: set[str] = set()


def is_admin(request: Request) -> bool:
    token = request.cookies.get("admin_token", "")
    return token in _admin_sessions


# ── Startup ───────────────────────────────────────────────────────────────────

@app.on_event("startup")
def _startup() -> None:
    Base.metadata.create_all(bind=engine)


# ── Landing ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse(
        "landing.html",
        {"request": request, "byline": "BY Clara Vialle"},
    )


@app.get("/init")
def init(db: OrmSession = Depends(get_db)):
    token = seed.upsert_seed(db=db)
    return RedirectResponse(url=f"/t/{token}/profil", status_code=302)


@app.post("/start")
def start(db: OrmSession = Depends(get_db)):
    token = seed.upsert_seed(db=db)
    return RedirectResponse(url=f"/t/{token}/profil", status_code=302)


# ── Profil candidat ───────────────────────────────────────────────────────────

@app.get("/t/{token}/profil", response_class=HTMLResponse)
def profil_form(token: str, request: Request, db: OrmSession = Depends(get_db)):
    sess = db.query(models.Session).filter(models.Session.token == token).first()
    if not sess:
        return templates.TemplateResponse("done.html", {"request": request, "message": "Lien invalide."}, status_code=404)
    return templates.TemplateResponse("profil.html", {"request": request, "token": token})


@app.post("/t/{token}/profil", response_class=HTMLResponse)
async def profil_save(token: str, request: Request, db: OrmSession = Depends(get_db)):
    sess = db.query(models.Session).filter(models.Session.token == token).first()
    if not sess:
        return templates.TemplateResponse("done.html", {"request": request, "message": "Lien invalide."}, status_code=404)

    form = await request.form()
    sess.prenom     = form.get("prenom", "").strip()
    sess.nom        = form.get("nom", "").strip()
    sess.role       = form.get("role", "").strip()
    sess.experience = form.get("experience", "").strip()
    sess.shop_type  = form.get("shop_type", "").strip()
    sess.consent    = bool(form.get("consent"))
    db.commit()

    return RedirectResponse(url=f"/t/{token}", status_code=302)


# ── Quiz ──────────────────────────────────────────────────────────────────────

@app.get("/t/{token}", response_class=HTMLResponse)
def take_quiz(token: str, request: Request, db: OrmSession = Depends(get_db)):
    sess = db.query(models.Session).filter(models.Session.token == token).first()
    if not sess:
        return templates.TemplateResponse("done.html", {"request": request, "message": "Lien invalide."}, status_code=404)

    if not sess.prenom:
        return RedirectResponse(url=f"/t/{token}/profil", status_code=302)

    quiz = db.query(models.Quiz).filter(models.Quiz.id == sess.quiz_id).first()
    if not quiz:
        return templates.TemplateResponse("done.html", {"request": request, "message": "Quiz introuvable."}, status_code=404)

    # Récupérer les questions tirées aléatoirement pour cette session
    try:
        chosen_ids = json.loads(sess.question_ids_json or "[]")
    except Exception:
        chosen_ids = []

    if chosen_ids:
        # Récupérer dans l'ordre du tirage
        questions_map = {
            q.id: q for q in
            db.query(models.Question).filter(models.Question.id.in_(chosen_ids)).all()
        }
        questions = [questions_map[qid] for qid in chosen_ids if qid in questions_map]
    else:
        # Fallback : toutes les questions dans l'ordre
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
        q_payload.append({"id": q.id, "kind": q.kind, "topic": q.topic, "text": q.text, "choices": choices})

    return templates.TemplateResponse(
        "quiz.html",
        {"request": request, "quiz_title": quiz.title, "token": token,
         "questions": q_payload, "prenom": sess.prenom},
    )


@app.post("/t/{token}", response_class=HTMLResponse)
async def submit_quiz(token: str, request: Request, db: OrmSession = Depends(get_db)):
    sess = db.query(models.Session).filter(models.Session.token == token).first()
    if not sess:
        return templates.TemplateResponse("done.html", {"request": request, "message": "Lien invalide."}, status_code=404)

    form = await request.form()

    # Récupérer exactement les mêmes questions que celles présentées
    try:
        chosen_ids = json.loads(sess.question_ids_json or "[]")
    except Exception:
        chosen_ids = []

    if chosen_ids:
        questions_map = {
            q.id: q for q in
            db.query(models.Question).filter(models.Question.id.in_(chosen_ids)).all()
        }
        questions = [questions_map[qid] for qid in chosen_ids if qid in questions_map]
    else:
        questions = (
            db.query(models.Question)
            .filter(models.Question.quiz_id == sess.quiz_id)
            .order_by(models.Question.id.asc())
            .all()
        )

    correct_count = 0
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
        if is_correct:
            correct_count += 1

        existing = (
            db.query(models.Answer)
            .filter(models.Answer.session_id == sess.id, models.Answer.question_id == q.id)
            .first()
        )
        if existing:
            existing.selected_json = json.dumps(selected_ids, ensure_ascii=False)
            existing.is_correct = is_correct
        else:
            db.add(models.Answer(
                session_id=sess.id,
                question_id=q.id,
                selected_json=json.dumps(selected_ids, ensure_ascii=False),
                is_correct=is_correct,
            ))

    db.commit()
    return templates.TemplateResponse("done.html", {
        "request": request,
        "message": f"Merci {sess.prenom} !",
        "correct": correct_count,
        "total": len(questions),
        "prenom": sess.prenom,
    })


# ── Admin — Login ─────────────────────────────────────────────────────────────

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_form(request: Request):
    if is_admin(request):
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request):
    form = await request.form()
    password = form.get("password", "")

    if password == ADMIN_PASSWORD:
        token = secrets.token_urlsafe(32)
        _admin_sessions.add(token)
        response = RedirectResponse(url="/admin", status_code=302)
        response.set_cookie("admin_token", token, httponly=True, samesite="lax", max_age=3600 * 8)
        return response

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Mot de passe incorrect."
    })


@app.get("/admin/logout")
def admin_logout(request: Request):
    token = request.cookies.get("admin_token", "")
    _admin_sessions.discard(token)
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("admin_token")
    return response


# ── Admin — Dashboard ─────────────────────────────────────────────────────────

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, db: OrmSession = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    sessions = db.query(models.Session).order_by(models.Session.id.desc()).limit(200).all()
    sessions_data = []
    for s in sessions:
        answers = db.query(models.Answer).filter(models.Answer.session_id == s.id).all()
        total_q = db.query(models.Question).filter(models.Question.quiz_id == s.quiz_id).count()
        correct = sum(1 for a in answers if a.is_correct)
        sessions_data.append({
            "session": s,
            "correct": correct,
            "total": total_q,
            "score_pct": round(correct / total_q * 100) if total_q else 0,
        })

    return templates.TemplateResponse("admin.html", {"request": request, "sessions_data": sessions_data})


@app.get("/admin/export.csv")
def export_csv(request: Request, db: OrmSession = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["date", "token", "prenom", "nom", "role", "experience", "type_magasin", "score", "total", "score_pct"])

    sessions = db.query(models.Session).order_by(models.Session.id.desc()).all()
    for s in sessions:
        answers = db.query(models.Answer).filter(models.Answer.session_id == s.id).all()
        total_q = db.query(models.Question).filter(models.Question.quiz_id == s.quiz_id).count()
        correct = sum(1 for a in answers if a.is_correct)
        pct = round(correct / total_q * 100) if total_q else 0
        w.writerow([s.created_at, s.token, s.prenom, s.nom, s.role, s.experience, s.shop_type, correct, total_q, pct])

    out.seek(0)
    return StreamingResponse(
        iter([out.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=podotest_resultats.csv"},
    )
