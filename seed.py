from __future__ import annotations

import json
import secrets

from sqlalchemy.orm import Session as OrmSession
from models import Quiz, Question, Session

NB_QUESTIONS = 15


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

        # ── FICHE 1 · Hallux Valgus ───────────────────────────────────
        {
            "kind": "single",
            "topic": "Hallux Valgus",
            "text": "Un client a un oignon douloureux sur le gros orteil. Quelle chaussure lui conseillez-vous ?",
            "choices": [
                {"id": "A", "label": "Cuir souple, avant-pied large, sans coutures ni œillets", "is_correct": True},
                {"id": "B", "label": "Bout pointu en verni pour maintenir l'orteil", "is_correct": False},
                {"id": "C", "label": "Basket synthétique bien ajustée", "is_correct": False},
                {"id": "D", "label": "Sandale à talon compensé", "is_correct": False},
            ],
        },
        {
            "kind": "multi",
            "topic": "Hallux Valgus",
            "text": "Quelles caractéristiques de chaussure sont à éviter pour un client avec un hallux valgus ? (plusieurs réponses)",
            "choices": [
                {"id": "A", "label": "Bout pointu ou étroit", "is_correct": True},
                {"id": "B", "label": "Talon haut", "is_correct": True},
                {"id": "C", "label": "Coutures ou œillets sur l'avant-pied", "is_correct": True},
                {"id": "D", "label": "Cuir souple avec avant-pied large", "is_correct": False},
            ],
        },

        # ── FICHE 2 · Mycose & Hygiène ───────────────────────────────
        {
            "kind": "single",
            "topic": "Mycose & Hygiène",
            "text": "Quelle matière de chaussure recommandez-vous à un client qui transpire beaucoup des pieds ?",
            "choices": [
                {"id": "A", "label": "Synthétique imperméable pour garder les pieds au sec", "is_correct": False},
                {"id": "B", "label": "Cuir naturel ou textile respirant", "is_correct": True},
                {"id": "C", "label": "Plastique souple facile à nettoyer", "is_correct": False},
                {"id": "D", "label": "Verni brillant", "is_correct": False},
            ],
        },
        {
            "kind": "multi",
            "topic": "Mycose & Hygiène",
            "text": "Pour limiter les mycoses, quels conseils donner sur la chaussure et les chaussettes ? (plusieurs réponses)",
            "choices": [
                {"id": "A", "label": "Alterner les chaussures chaque jour pour les laisser sécher", "is_correct": True},
                {"id": "B", "label": "Porter des chaussettes en coton ou laine, changées chaque jour", "is_correct": True},
                {"id": "C", "label": "Choisir une chaussure en matière respirante", "is_correct": True},
                {"id": "D", "label": "Garder toujours la même paire pour un meilleur maintien", "is_correct": False},
            ],
        },

        # ── FICHE 3 · Épine calcanéenne ──────────────────────────────
        {
            "kind": "single",
            "topic": "Épine calcanéenne",
            "text": "Un client a mal sous le talon dès le matin. Quelle semelle lui proposer en priorité ?",
            "choices": [
                {"id": "A", "label": "Semelle plate et rigide pour stabiliser", "is_correct": False},
                {"id": "B", "label": "Semelle avec amorti sous le talon et évidement sous la zone douloureuse", "is_correct": True},
                {"id": "C", "label": "Semelle surélevée à l'avant pour décharger le talon", "is_correct": False},
                {"id": "D", "label": "Semelle de sport standard", "is_correct": False},
            ],
        },

        # ── FICHE 4 · Ongle incarné ──────────────────────────────────
        {
            "kind": "single",
            "topic": "Ongle incarné",
            "text": "Un client souffre régulièrement d'ongles incarnés. Quelle chaussure lui évite d'aggraver le problème ?",
            "choices": [
                {"id": "A", "label": "Chaussure étroite à bout pointu pour bien tenir l'orteil", "is_correct": False},
                {"id": "B", "label": "Chaussure large avec empeigne haute sans coutures sur les orteils", "is_correct": True},
                {"id": "C", "label": "Chaussure à talon pour reporter le poids vers l'arrière", "is_correct": False},
                {"id": "D", "label": "Mule ouverte à l'arrière", "is_correct": False},
            ],
        },

        # ── FICHE 5 · Pied plat ──────────────────────────────────────
        {
            "kind": "single",
            "topic": "Pied plat",
            "text": "Un client avec un pied plat douloureux cherche une chaussure de ville. Laquelle lui conseillez-vous ?",
            "choices": [
                {"id": "A", "label": "Chaussure souple en tissu pour ne pas contraindre le pied", "is_correct": False},
                {"id": "B", "label": "Chaussure rigide en cuir avec bon maintien de la voûte", "is_correct": True},
                {"id": "C", "label": "Tong légère pour laisser le pied libre", "is_correct": False},
                {"id": "D", "label": "Mocassin souple sans soutien", "is_correct": False},
            ],
        },
        {
            "kind": "single",
            "topic": "Pied plat",
            "text": "Pour un client avec pied plat, quel type de semelle intérieure est le plus indiqué ?",
            "choices": [
                {"id": "A", "label": "Semelle plate sans relief", "is_correct": False},
                {"id": "B", "label": "Semelle avec soutien de la voûte plantaire côté interne", "is_correct": True},
                {"id": "C", "label": "Semelle rembourrée uniquement sous le talon", "is_correct": False},
                {"id": "D", "label": "Semelle de sport universelle", "is_correct": False},
            ],
        },

        # ── FICHE 6 · Pied creux ─────────────────────────────────────
        {
            "kind": "single",
            "topic": "Pied creux",
            "text": "Un client a un pied creux avec des douleurs à l'avant-pied. Quelle caractéristique de chaussure est prioritaire ?",
            "choices": [
                {"id": "A", "label": "Chaussure plate et souple sans soutien pour laisser le pied s'adapter", "is_correct": False},
                {"id": "B", "label": "Chaussure avec un petit talon pour décharger l'avant-pied et sans coutures", "is_correct": True},
                {"id": "C", "label": "Chaussure rigide à semelle plate", "is_correct": False},
                {"id": "D", "label": "Chaussure de sport avec semelle épaisse uniforme", "is_correct": False},
            ],
        },

        # ── FICHE 7 · Griffes d'orteils ──────────────────────────────
        {
            "kind": "multi",
            "topic": "Griffes d'orteils",
            "text": "Un client a les orteils en griffes avec des cors sur le dessus. Quels critères sont indispensables dans le choix de la chaussure ? (plusieurs réponses)",
            "choices": [
                {"id": "A", "label": "Empeigne haute pour ne pas frotter sur les orteils", "is_correct": True},
                {"id": "B", "label": "Matière souple sans coutures au-dessus des orteils", "is_correct": True},
                {"id": "C", "label": "Eviter les talons hauts qui aggravent la déformation", "is_correct": True},
                {"id": "D", "label": "Bout pointu pour maintenir les orteils alignés", "is_correct": False},
            ],
        },

        # ── FICHE 8 · Varices & Œdèmes ───────────────────────────────
        {
            "kind": "multi",
            "topic": "Varices & Œdèmes",
            "text": "Un client a les jambes lourdes et les pieds qui gonflent en fin de journée. Que lui recommandez-vous ? (plusieurs réponses)",
            "choices": [
                {"id": "A", "label": "Des chaussettes ou bas de compression", "is_correct": True},
                {"id": "B", "label": "Une chaussure avec lacets ou velcro ajustables pour s'adapter au gonflement", "is_correct": True},
                {"id": "C", "label": "Une semelle favorisant le retour veineux", "is_correct": True},
                {"id": "D", "label": "Une chaussure serrée pour soutenir la cheville", "is_correct": False},
            ],
        },
        {
            "kind": "single",
            "topic": "Varices & Œdèmes",
            "text": "Quel type de chaussette est le plus adapté pour un client souffrant de varices ?",
            "choices": [
                {"id": "A", "label": "Chaussette fine en nylon", "is_correct": False},
                {"id": "B", "label": "Chaussette de compression en coton ou microfibre", "is_correct": True},
                {"id": "C", "label": "Chaussette épaisse en laine", "is_correct": False},
                {"id": "D", "label": "Chaussette courte type socquette", "is_correct": False},
            ],
        },

        # ── FICHE 9 · Genu valgum / varum ────────────────────────────
        {
            "kind": "single",
            "topic": "Genu valgum / varum",
            "text": "Un client a les genoux en X (genu valgum). Quel élément de semelle orthopédique est indiqué pour corriger l'appui ?",
            "choices": [
                {"id": "A", "label": "Elément pronateur côté interne (soutien de la voûte)", "is_correct": False},
                {"id": "B", "label": "Elément supinateur côté externe (rehausse latérale externe)", "is_correct": True},
                {"id": "C", "label": "Semelle neutre sans correction", "is_correct": False},
                {"id": "D", "label": "Semelle avec amorti uniquement sous le talon", "is_correct": False},
            ],
        },

        # ── FICHE 10 · Cors & Durillons ──────────────────────────────
        {
            "kind": "multi",
            "topic": "Cors & Durillons",
            "text": "Un client revient avec un cor apparu depuis qu'il porte ses nouvelles chaussures. Quelles zones de la chaussure vérifiez-vous ? (plusieurs réponses)",
            "choices": [
                {"id": "A", "label": "Les coutures intérieures qui peuvent frotter", "is_correct": True},
                {"id": "B", "label": "La largeur de l'avant-pied par rapport au pied du client", "is_correct": True},
                {"id": "C", "label": "La hauteur de l'empeigne au niveau des orteils", "is_correct": True},
                {"id": "D", "label": "La couleur du cuir extérieur", "is_correct": False},
            ],
        },

        # ── FICHE 11 · Verrues ────────────────────────────────────────
        {
            "kind": "single",
            "topic": "Verrues plantaires",
            "text": "Un client fréquente régulièrement la piscine et a des verrues plantaires. Quel conseil de chaussage lui donner ?",
            "choices": [
                {"id": "A", "label": "Porter des chaussures imperméables en permanence", "is_correct": False},
                {"id": "B", "label": "Porter des sandales ou claquettes de piscine dans les zones communes humides", "is_correct": True},
                {"id": "C", "label": "Marcher pieds nus pour endurcir la peau", "is_correct": False},
                {"id": "D", "label": "Porter des chaussettes épaisses à la piscine", "is_correct": False},
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
