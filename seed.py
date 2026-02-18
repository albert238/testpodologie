from __future__ import annotations

import json
import secrets
from typing import Optional

from sqlalchemy.orm import Session as OrmSession

from models import Quiz, Question, Session


def upsert_seed(db: OrmSession) -> str:
    """
    Crée le quiz + 2 questions si besoin, puis crée une session (token).
    Retourne le token.
    """

    # 1) Trouver / créer le quiz
    quiz = db.query(Quiz).filter(Quiz.slug == "demo").first()
    if quiz is None:
        quiz = Quiz(
            title="Podologie • Formation vendeurs",
            slug="demo",
            author="Clara Vialle",
            is_active=True,
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
    else:
        quiz.is_active = True
        db.commit()

    # 2) Ajouter des questions uniquement si le quiz est vide
    existing = db.query(Question).filter(Question.quiz_id == quiz.id).count()
    if existing == 0:
        q1 = Question(
            quiz_id=quiz.id,
            kind="single",
            topic="pathologies",
            text="Chez un client diabétique, quel point est le plus important ?",
            choices_json=json.dumps(
                [
                    {
                        "id": "A",
                        "label": "Privilégier une chaussure très serrée pour le maintien",
                        "is_correct": False,
                        "feedback": "Trop serré = risque de plaies / mauvaise circulation.",
                    },
                    {
                        "id": "B",
                        "label": "Limiter les points de pression et vérifier le chaussant",
                        "is_correct": True,
                        "feedback": "Oui : réduire frottements/pressions + vérifier le chaussant.",
                    },
                    {
                        "id": "C",
                        "label": "Choisir surtout une semelle très fine",
                        "is_correct": False,
                        "feedback": "Ce n’est pas le critère principal.",
                    },
                ],
                ensure_ascii=False,
            ),
        )

        q2 = Question(
            quiz_id=quiz.id,
            kind="multi",
            topic="conseil",
            text="Coche les bonnes pratiques lors de l’essayage :",
            choices_json=json.dumps(
                [
                    {
                        "id": "A",
                        "label": "Faire essayer en fin de journée si possible",
                        "is_correct": True,
                        "feedback": "Oui : le pied gonfle souvent en fin de journée.",
                    },
                    {
                        "id": "B",
                        "label": "Ignorer les douleurs si la chaussure est jolie",
                        "is_correct": False,
                        "feedback": "Non : la douleur est un signal d’alerte.",
                    },
                    {
                        "id": "C",
                        "label": "Vérifier l’espace à l’avant (orteils)",
                        "is_correct": True,
                        "feedback": "Oui : éviter compression des orteils.",
                    },
                    {
                        "id": "D",
                        "label": "Forcer pour “faire” la chaussure",
                        "is_correct": False,
                        "feedback": "Non : risque de blessures.",
                    },
                ],
                ensure_ascii=False,
            ),
        )

        db.add_all([q1, q2])
        db.commit()

    # 3) Créer une session token
    token = secrets.token_urlsafe(10)
    s = Session(token=token, quiz_id=quiz.id)
    db.add(s)
    db.commit()

    return token
