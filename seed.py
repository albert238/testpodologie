from __future__ import annotations

import json
import secrets

from sqlalchemy.orm import Session as OrmSession

from models import Quiz, Question, Session


def upsert_seed(db: OrmSession) -> str:
    """
    Crée le quiz + 5 questions si besoin, puis crée une session (token).
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

    # 2) Ajouter les questions uniquement si le quiz est vide
    existing = db.query(Question).filter(Question.quiz_id == quiz.id).count()
    if existing == 0:

        questions_data = [
            {
                "kind": "single",
                "topic": "Pathologies",
                "text": "Chez un client diabétique, quel point est le plus important lors du choix d'une chaussure ?",
                "choices": [
                    {"id": "A", "label": "Privilégier une chaussure très serrée pour un meilleur maintien", "is_correct": False, "feedback": "Trop serré = risque de plaies et mauvaise circulation."},
                    {"id": "B", "label": "Limiter les points de pression et vérifier l'adaptation du chaussant", "is_correct": True, "feedback": "Oui : réduire frottements et pressions est essentiel chez le client diabétique."},
                    {"id": "C", "label": "Choisir avant tout une semelle très fine pour la sensibilité", "is_correct": False, "feedback": "Ce n'est pas le critère principal."},
                    {"id": "D", "label": "La matière importe peu, seul le style compte", "is_correct": False, "feedback": "La matière et le chaussant sont primordiaux."},
                ],
            },
            {
                "kind": "multi",
                "topic": "Conseil à l'essayage",
                "text": "Cochez les bonnes pratiques lors de l'essayage d'une chaussure :",
                "choices": [
                    {"id": "A", "label": "Faire essayer en fin de journée si possible", "is_correct": True, "feedback": "Oui : le pied gonfle souvent en fin de journée."},
                    {"id": "B", "label": "Ignorer les douleurs si la chaussure est jolie", "is_correct": False, "feedback": "Non : la douleur est toujours un signal d'alerte."},
                    {"id": "C", "label": "Vérifier l'espace libre à l'avant (orteils)", "is_correct": True, "feedback": "Oui : un espace d'environ 1 cm prévient la compression des orteils."},
                    {"id": "D", "label": "Forcer pour faire la chaussure", "is_correct": False, "feedback": "Non : forcer provoque des blessures et des déformations."},
                ],
            },
            {
                "kind": "single",
                "topic": "Morphologie du pied",
                "text": "Un client présente un hallux valgus (oignon). Quelle chaussure lui recommandez-vous en priorité ?",
                "choices": [
                    {"id": "A", "label": "Une chaussure à bout pointu pour élancer la silhouette", "is_correct": False, "feedback": "Le bout pointu comprime l'avant-pied et aggrave l'hallux valgus."},
                    {"id": "B", "label": "Une chaussure à bout large ou rond avec tige souple", "is_correct": True, "feedback": "Oui : un avant-pied large et une tige souple réduisent la pression sur l'oignon."},
                    {"id": "C", "label": "Une chaussure à talon haut pour limiter l'appui", "is_correct": False, "feedback": "Le talon haut reporte le poids sur l'avant-pied et aggrave la douleur."},
                    {"id": "D", "label": "N'importe quelle chaussure, cela n'a pas d'impact", "is_correct": False, "feedback": "La morphologie du pied doit toujours guider le choix."},
                ],
            },
            {
                "kind": "multi",
                "topic": "Mesure & pointure",
                "text": "Quels éléments devez-vous mesurer ou vérifier pour conseiller la bonne pointure ?",
                "choices": [
                    {"id": "A", "label": "La longueur du pied (talon à l'orteil le plus long)", "is_correct": True, "feedback": "Indispensable : c'est la base du choix de pointure."},
                    {"id": "B", "label": "La largeur de l'avant-pied", "is_correct": True, "feedback": "Oui : un pied large ou étroit nécessite une largeur adaptée."},
                    {"id": "C", "label": "La couleur des chaussettes du client", "is_correct": False, "feedback": "La couleur des chaussettes n'a aucune incidence."},
                    {"id": "D", "label": "Le type de semelle intérieure (épaisseur, orthèse éventuelle)", "is_correct": True, "feedback": "Oui : une semelle orthopédique peut nécessiter une pointure supplémentaire."},
                ],
            },
            {
                "kind": "single",
                "topic": "Prévention & hygiène",
                "text": "Un client se plaint de mycoses récurrentes aux pieds. Quel conseil prioritaire lui donnez-vous ?",
                "choices": [
                    {"id": "A", "label": "Porter des chaussures en matières synthétiques imperméables", "is_correct": False, "feedback": "Les matières synthétiques favorisent la transpiration et les mycoses."},
                    {"id": "B", "label": "Choisir des matières respirantes et alterner les chaussures chaque jour", "is_correct": True, "feedback": "Oui : laisser sécher les chaussures 24h entre deux ports limite fortement les récidives."},
                    {"id": "C", "label": "Porter les mêmes chaussures tous les jours pour les assouplir", "is_correct": False, "feedback": "Cela maintient l'humidité et favorise les champignons."},
                    {"id": "D", "label": "Éviter les chaussettes pour que le pied respire mieux", "is_correct": False, "feedback": "Les chaussettes en fibres naturelles absorbent la transpiration et protègent."},
                ],
            },
        ]

        for qd in questions_data:
            db.add(Question(
                quiz_id=quiz.id,
                kind=qd["kind"],
                topic=qd["topic"],
                text=qd["text"],
                choices_json=json.dumps(qd["choices"], ensure_ascii=False),
            ))
        db.commit()

    # 3) Créer une session token
    token = secrets.token_urlsafe(10)
    s = Session(token=token, quiz_id=quiz.id)
    db.add(s)
    db.commit()

    return token
