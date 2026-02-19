from __future__ import annotations

import json
import secrets

from sqlalchemy.orm import Session as OrmSession
from models import Quiz, Question, Session

NB_QUESTIONS = 5


def ensure_questions(db: OrmSession) -> None:
    quiz = db.query(Quiz).filter(Quiz.slug == "demo").first()
    if quiz is None:
        quiz = Quiz(
            title="PodoTest • Formation vendeurs",
            slug="demo",
            author="Clara Vialle",
            is_active=True,
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
    existing = db.query(Question).filter(Question.quiz_id == quiz.id).count()
    if existing == 0:
        _insert_questions(db, quiz.id)


def upsert_seed(db: OrmSession) -> str:
    import random
    quiz = db.query(Quiz).filter(Quiz.slug == "demo").first()
    if quiz is None:
        quiz = Quiz(
            title="PodoTest • Formation vendeurs",
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

    existing = db.query(Question).filter(Question.quiz_id == quiz.id).count()
    if existing == 0:
        _insert_questions(db, quiz.id)

    all_ids = [row[0] for row in db.query(Question.id).filter(Question.quiz_id == quiz.id).all()]
    chosen_ids = random.sample(all_ids, min(NB_QUESTIONS, len(all_ids)))

    token = secrets.token_urlsafe(10)
    s = Session(token=token, quiz_id=quiz.id, question_ids_json=json.dumps(chosen_ids))
    db.add(s)
    db.commit()
    return token


def _insert_questions(db: OrmSession, quiz_id: int) -> None:
    questions_data = [

        # Q1 — Hallux Valgus
        {
            "kind": "single",
            "topic": "Hallux Valgus",
            "text": "Un client a un hallux valgus (oignon au gros orteil). Quelle chaussure lui recommandez-vous ?",
            "choices": [
                {"id": "A", "label": "Chaussure bout pointu avec talon haut", "is_correct": False},
                {"id": "B", "label": "Chaussure large, cuir souple, sans coutures ni œillets", "is_correct": True},
                {"id": "C", "label": "Chaussure de sport synthétique", "is_correct": False},
                {"id": "D", "label": "Sandale à talon compensé", "is_correct": False},
            ],
        },

        # Q2 — Mycose
        {
            "kind": "multi",
            "topic": "Mycose & Hygiène",
            "text": "Un client a souvent des mycoses aux pieds. Quels conseils lui donner ? (plusieurs réponses)",
            "choices": [
                {"id": "A", "label": "Bien sécher entre les orteils après la douche", "is_correct": True},
                {"id": "B", "label": "Garder toujours les mêmes chaussures fermées", "is_correct": False},
                {"id": "C", "label": "Changer les chaussettes souvent et les laver à 60 °C", "is_correct": True},
                {"id": "D", "label": "Alterner ses chaussures pour les laisser sécher", "is_correct": True},
            ],
        },

        # Q3 — Épine calcanéenne
        {
            "kind": "single",
            "topic": "Épine calcanéenne",
            "text": "Un client a mal sous le talon, surtout le matin au lever. Parmi ces facteurs, lequel vient de l'extérieur (facteur externe) ?",
            "choices": [
                {"id": "A", "label": "Avoir un pied creux", "is_correct": False},
                {"id": "B", "label": "Être en surpoids", "is_correct": False},
                {"id": "C", "label": "Porter de mauvaises chaussures", "is_correct": True},
                {"id": "D", "label": "Avoir un centre de gravité mal placé", "is_correct": False},
            ],
        },

        # Q4 — Ongle incarné
        {
            "kind": "multi",
            "topic": "Ongle incarné",
            "text": "Quelles sont les causes courantes d'un ongle incarné ? (plusieurs réponses)",
            "choices": [
                {"id": "A", "label": "Couper les ongles trop courts ou arrondis", "is_correct": True},
                {"id": "B", "label": "Porter des chaussures trop serrées", "is_correct": True},
                {"id": "C", "label": "Marcher pieds nus sur la plage", "is_correct": False},
                {"id": "D", "label": "Avoir un ongle très courbé", "is_correct": True},
            ],
        },

        # Q5 — Pied plat
        {
            "kind": "single",
            "topic": "Pied plat",
            "text": "Un client a un pied plat douloureux. Quelle chaussure évite d'aggraver le problème ?",
            "choices": [
                {"id": "A", "label": "Chaussure souple en tissu", "is_correct": False},
                {"id": "B", "label": "Chaussure rigide en cuir avec bon maintien", "is_correct": True},
                {"id": "C", "label": "Tong légère pour ne pas contraindre le pied", "is_correct": False},
                {"id": "D", "label": "Chaussure sans coutures avec petit talon", "is_correct": False},
            ],
        },

        # Q6 — Pied creux
        {
            "kind": "multi",
            "topic": "Pied creux",
            "text": "Quels problèmes sont souvent causés par un pied creux ? (plusieurs réponses)",
            "choices": [
                {"id": "A", "label": "Entorses de cheville à répétition", "is_correct": True},
                {"id": "B", "label": "Pronation excessive (pied qui s'écrase vers l'intérieur)", "is_correct": False},
                {"id": "C", "label": "Griffes d'orteils", "is_correct": True},
                {"id": "D", "label": "Durillons sous le talon et l'avant-pied", "is_correct": True},
            ],
        },

        # Q7 — Griffes d'orteils
        {
            "kind": "single",
            "topic": "Griffes d'orteils",
            "text": "Un client a les orteils en griffes. Quel est le critère le plus important dans le choix de la chaussure ?",
            "choices": [
                {"id": "A", "label": "Une semelle très amortissante", "is_correct": False},
                {"id": "B", "label": "Une empeigne haute pour éviter le frottement sur les orteils", "is_correct": True},
                {"id": "C", "label": "Un talon haut pour soulager l'avant-pied", "is_correct": False},
                {"id": "D", "label": "Une chaussure étroite pour maintenir les orteils", "is_correct": False},
            ],
        },

        # Q8 — Varices
        {
            "kind": "multi",
            "topic": "Varices & Œdèmes",
            "text": "Un client souffre de jambes lourdes et de varices. Que lui conseillez-vous ? (plusieurs réponses)",
            "choices": [
                {"id": "A", "label": "Des bas de compression", "is_correct": True},
                {"id": "B", "label": "Des chaussures très serrées pour soutenir la cheville", "is_correct": False},
                {"id": "C", "label": "Des semelles adaptées au retour veineux", "is_correct": True},
                {"id": "D", "label": "Bouger régulièrement, marcher", "is_correct": True},
            ],
        },

        # Q9 — Genu valgum/varum
        {
            "kind": "single",
            "topic": "Genu valgum / varum",
            "text": "Un client a les genoux en X (genu valgum). Quel type de semelle orthopédique est indiqué ?",
            "choices": [
                {"id": "A", "label": "Semelle avec éléments pronateurs (soutien côté intérieur)", "is_correct": False},
                {"id": "B", "label": "Semelle avec éléments supinateurs (soutien côté extérieur)", "is_correct": True},
                {"id": "C", "label": "Semelle molle sans correction", "is_correct": False},
                {"id": "D", "label": "Aucune semelle, seule la chirurgie aide", "is_correct": False},
            ],
        },

        # Q10 — Cors
        {
            "kind": "single",
            "topic": "Cors & Durillons",
            "text": "Qu'est-ce qui provoque la formation d'un cor sur le pied ?",
            "choices": [
                {"id": "A", "label": "Une infection de la peau", "is_correct": False},
                {"id": "B", "label": "Un frottement ou une pression répétée au même endroit", "is_correct": True},
                {"id": "C", "label": "Un manque de vitamines", "is_correct": False},
                {"id": "D", "label": "Une allergie au cuir", "is_correct": False},
            ],
        },

        # Q11 — Verrues
        {
            "kind": "multi",
            "topic": "Verrues plantaires",
            "text": "Où attrape-t-on le plus souvent des verrues plantaires ? (plusieurs réponses)",
            "choices": [
                {"id": "A", "label": "À la piscine", "is_correct": True},
                {"id": "B", "label": "Dans les vestiaires communs", "is_correct": True},
                {"id": "C", "label": "En portant des chaussures en cuir", "is_correct": False},
                {"id": "D", "label": "En salle de fitness", "is_correct": True},
            ],
        },

    ]

    for qd in questions_data:
        db.add(Question(
            quiz_id=quiz_id,
            kind=qd["kind"],
            topic=qd["topic"],
            text=qd["text"],
            choices_json=json.dumps(qd["choices"], ensure_ascii=False),
        ))
    db.commit()
