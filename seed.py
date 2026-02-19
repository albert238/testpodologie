from __future__ import annotations

import json
import secrets

from sqlalchemy.orm import Session as OrmSession

from models import Quiz, Question, Session

# Nombre de questions tirées aléatoirement par session
NB_QUESTIONS = 5


def upsert_seed(db: OrmSession) -> str:
    """
    Crée le quiz + 11 questions si besoin.
    Tire NB_QUESTIONS aléatoirement et crée une session.
    Retourne le token.
    """
    import random

    # 1) Trouver / créer le quiz
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

    # 2) Insérer les 11 questions si le quiz est vide
    existing = db.query(Question).filter(Question.quiz_id == quiz.id).count()
    if existing == 0:
        _insert_questions(db, quiz.id)

    # 3) Tirer NB_QUESTIONS aléatoirement parmi toutes les questions
    all_ids = [
        row[0] for row in
        db.query(Question.id).filter(Question.quiz_id == quiz.id).all()
    ]
    chosen_ids = random.sample(all_ids, min(NB_QUESTIONS, len(all_ids)))

    # 4) Créer la session avec les IDs mémorisés
    token = secrets.token_urlsafe(10)
    s = Session(
        token=token,
        quiz_id=quiz.id,
        question_ids_json=json.dumps(chosen_ids),
    )
    db.add(s)
    db.commit()

    return token


def _insert_questions(db: OrmSession, quiz_id: int) -> None:
    questions_data = [

        # ── Q01 — Hallux Valgus ──────────────────────────────────────────────
        {
            "kind": "single",
            "topic": "Hallux Valgus",
            "text": (
                "Un client présente un hallux valgus (oignon au pied). "
                "Quel type de chaussure est le plus adapté à lui conseiller ?"
            ),
            "choices": [
                {
                    "id": "A",
                    "label": "Chaussure à bout pointu et talon haut",
                    "is_correct": False,
                    "feedback": "Le bout pointu comprime l'avant-pied et le talon haut aggrave la déviation de l'orteil.",
                },
                {
                    "id": "B",
                    "label": "Chaussure à haute empeigne, cuir souple, sans œillets ni coutures, avant-pied large",
                    "is_correct": True,
                    "feedback": "Correct ! Ces critères évitent le frottement sur l'exostose et limitent la déviation. (Fiche Hallux Valgus – Calcéologie)",
                },
                {
                    "id": "C",
                    "label": "Chaussure souple en tissu synthétique, peu importe la largeur",
                    "is_correct": False,
                    "feedback": "Non : la largeur de l'avant-pied et l'absence de coutures sont essentielles.",
                },
                {
                    "id": "D",
                    "label": "Sandales ouvertes à talon compensé",
                    "is_correct": False,
                    "feedback": "Ce n'est pas le conseil prioritaire ; le talon compensé reste problématique.",
                },
            ],
        },

        # ── Q02 — Mycose ─────────────────────────────────────────────────────
        {
            "kind": "multi",
            "topic": "Mycose & Hygiène",
            "text": (
                "Quels conseils donnez-vous à un client souffrant de mycoses "
                "récurrentes aux pieds ? (plusieurs réponses correctes)"
            ),
            "choices": [
                {
                    "id": "A",
                    "label": "Bien sécher les pieds entre les orteils après la douche",
                    "is_correct": True,
                    "feedback": "Oui ! L'humidité est le principal facteur favorisant la mycose.",
                },
                {
                    "id": "B",
                    "label": "Porter toujours les mêmes chaussures fermées pour protéger les pieds",
                    "is_correct": False,
                    "feedback": "Non : il faut alterner les chaussures et privilégier des matières respirantes.",
                },
                {
                    "id": "C",
                    "label": "Changer les chaussettes régulièrement et les laver à 60 °C",
                    "is_correct": True,
                    "feedback": "Correct ! Laver à 60 °C élimine les champignons microscopiques.",
                },
                {
                    "id": "D",
                    "label": "Alterner les chaussures pour leur laisser le temps de sécher",
                    "is_correct": True,
                    "feedback": "Oui ! Alterner réduit l'humidité résiduelle et limite les récidives.",
                },
            ],
        },

        # ── Q03 — Épine calcanéenne ──────────────────────────────────────────
        {
            "kind": "single",
            "topic": "Épine calcanéenne",
            "text": (
                "Un client se plaint d'une douleur sous le talon, aggravée au réveil "
                "et à la marche. Parmi ces propositions, laquelle est un facteur "
                "EXTERNE reconnu de l'épine calcanéenne ?"
            ),
            "choices": [
                {
                    "id": "A",
                    "label": "Un pied creux",
                    "is_correct": False,
                    "feedback": "Le pied creux est un facteur interne (trouble statique), pas externe.",
                },
                {
                    "id": "B",
                    "label": "Un mauvais chaussage",
                    "is_correct": True,
                    "feedback": "Exact ! Le mauvais chaussage est cité parmi les facteurs externes. (Fiche Épine calcanéenne)",
                },
                {
                    "id": "C",
                    "label": "L'obésité",
                    "is_correct": False,
                    "feedback": "L'obésité est un facteur interne (surcharge mécanique).",
                },
                {
                    "id": "D",
                    "label": "Un centre de gravité postériorisé",
                    "is_correct": False,
                    "feedback": "C'est également un facteur interne biomécanique.",
                },
            ],
        },

        # ── Q04 — Ongle incarné ──────────────────────────────────────────────
        {
            "kind": "multi",
            "topic": "Ongle incarné",
            "text": (
                "Quelles sont les causes directes favorisant l'ongle incarné ? "
                "(plusieurs réponses correctes)"
            ),
            "choices": [
                {
                    "id": "A",
                    "label": "Couper les ongles trop courts ou en arrondi",
                    "is_correct": True,
                    "feedback": "Oui : un soin inadéquat des ongles est l'une des premières causes citées.",
                },
                {
                    "id": "B",
                    "label": "Le port de chaussures trop serrées",
                    "is_correct": True,
                    "feedback": "Correct ! La compression de l'ongle favorise directement l'incarnation.",
                },
                {
                    "id": "C",
                    "label": "Marcher pieds nus sur la plage",
                    "is_correct": False,
                    "feedback": "Marcher pieds nus n'est pas cité comme cause directe dans les fiches.",
                },
                {
                    "id": "D",
                    "label": "Une hypercourbure de l'ongle",
                    "is_correct": True,
                    "feedback": "Oui ! L'hypercourbure est explicitement mentionnée comme facteur favorisant.",
                },
            ],
        },

        # ── Q05 — Pied plat ──────────────────────────────────────────────────
        {
            "kind": "single",
            "topic": "Pied plat",
            "text": (
                "Un client a un pied plat douloureux. "
                "Quelle chaussure lui conseillez-vous en priorité ?"
            ),
            "choices": [
                {
                    "id": "A",
                    "label": "Une chaussure souple en tissu pour plus de confort",
                    "is_correct": False,
                    "feedback": "Non : les chaussures souples accentuent l'affaissement de la voûte plantaire.",
                },
                {
                    "id": "B",
                    "label": "Une chaussure rigide en cuir qui maintient correctement le pied",
                    "is_correct": True,
                    "feedback": "Exact ! Les chaussures rigides en cuir évitent d'accentuer l'affaissement. (Fiche Pied plat)",
                },
                {
                    "id": "C",
                    "label": "Une chaussure sans coutures avec un petit talon",
                    "is_correct": False,
                    "feedback": "Cette recommandation correspond au pied creux, pas au pied plat.",
                },
                {
                    "id": "D",
                    "label": "Des tongs pour ne pas contraindre le pied",
                    "is_correct": False,
                    "feedback": "Les tongs n'offrent aucun maintien et aggravent l'affaissement.",
                },
            ],
        },

        # ── Q06 — Pied creux ─────────────────────────────────────────────────
        {
            "kind": "multi",
            "topic": "Pied creux",
            "text": (
                "Quels symptômes sont caractéristiques du pied creux ? "
                "(plusieurs réponses correctes)"
            ),
            "choices": [
                {
                    "id": "A",
                    "label": "Entorses de chevilles à répétition",
                    "is_correct": True,
                    "feedback": "Oui ! L'instabilité liée au pied creux favorise les entorses répétées.",
                },
                {
                    "id": "B",
                    "label": "Pronation excessive",
                    "is_correct": False,
                    "feedback": "La pronation excessive est caractéristique du pied plat, pas du pied creux.",
                },
                {
                    "id": "C",
                    "label": "Griffes d'orteils et métatarsalgies",
                    "is_correct": True,
                    "feedback": "Correct ! Le pied creux entraîne fréquemment griffes d'orteils et douleurs sous l'avant-pied.",
                },
                {
                    "id": "D",
                    "label": "Kératose au talon et à l'avant-pied",
                    "is_correct": True,
                    "feedback": "Oui ! Les zones d'appui excessives du pied creux créent de la kératose.",
                },
            ],
        },

        # ── Q07 — Griffes d'orteils ──────────────────────────────────────────
        {
            "kind": "single",
            "topic": "Griffes d'orteils",
            "text": (
                "Un client a des griffes d'orteils. "
                "Quelle caractéristique de chaussure est prioritaire pour éviter les complications ?"
            ),
            "choices": [
                {
                    "id": "A",
                    "label": "Une semelle très amortissante",
                    "is_correct": False,
                    "feedback": "L'amorti n'est pas le critère prioritaire pour les griffes d'orteils.",
                },
                {
                    "id": "B",
                    "label": "Une empeigne assez haute pour éviter le frottement des orteils",
                    "is_correct": True,
                    "feedback": "Correct ! Une empeigne haute évite le frottement dorsal qui crée des cors et risques d'infection. (Fiche Griffes d'orteils – Calcéologie)",
                },
                {
                    "id": "C",
                    "label": "Un talon haut pour réduire l'appui avant",
                    "is_correct": False,
                    "feedback": "Non : les talons hauts favorisent au contraire la déformation des orteils.",
                },
                {
                    "id": "D",
                    "label": "Une chaussure étroite pour maintenir les orteils en place",
                    "is_correct": False,
                    "feedback": "Une chaussure étroite aggrave le frottement et risque de créer des cors dorsaux.",
                },
            ],
        },

        # ── Q08 — Varices & Œdèmes ───────────────────────────────────────────
        {
            "kind": "multi",
            "topic": "Varices & Œdèmes",
            "text": (
                "Un client souffre de varices et d'œdèmes aux jambes. "
                "Quels conseils liés au chaussage ou aux accessoires sont pertinents ? "
                "(plusieurs réponses correctes)"
            ),
            "choices": [
                {
                    "id": "A",
                    "label": "Recommander des bas de compression",
                    "is_correct": True,
                    "feedback": "Oui ! Les bas de compression favorisent le retour veineux. (Fiche Varices & Œdèmes)",
                },
                {
                    "id": "B",
                    "label": "Conseiller des semelles adaptées pour le retour veineux",
                    "is_correct": True,
                    "feedback": "Correct ! Des semelles spécifiques peuvent améliorer la dynamique veineuse à la marche.",
                },
                {
                    "id": "C",
                    "label": "Proposer des chaussures très serrées pour comprimer les vaisseaux",
                    "is_correct": False,
                    "feedback": "Non : des chaussures trop serrées aggravent la stase veineuse et les douleurs.",
                },
                {
                    "id": "D",
                    "label": "Encourager l'activité physique pour améliorer le retour veineux",
                    "is_correct": True,
                    "feedback": "Oui ! L'activité physique est citée en premier traitement hygiéno-diététique.",
                },
            ],
        },

        # ── Q09 — Genu valgum / varum ────────────────────────────────────────
        {
            "kind": "single",
            "topic": "Genu valgum / varum",
            "text": (
                "Un client présente un genu valgum (genoux en X). "
                "Quel type de correction podologique est indiqué ?"
            ),
            "choices": [
                {
                    "id": "A",
                    "label": "Des semelles avec éléments pronateurs",
                    "is_correct": False,
                    "feedback": "Les éléments pronateurs sont indiqués pour le genu varum (jambes arquées), pas le valgum.",
                },
                {
                    "id": "B",
                    "label": "Des semelles avec éléments supinateurs",
                    "is_correct": True,
                    "feedback": "Correct ! Pour le genu valgum, les semelles supinateurs ont un objectif antalgique sur le genou. (Fiche Genu valgum/varum)",
                },
                {
                    "id": "C",
                    "label": "Des semelles molles sans correction",
                    "is_correct": False,
                    "feedback": "Des semelles sans correction ne traitent pas le trouble statique sous-jacent.",
                },
                {
                    "id": "D",
                    "label": "Aucune semelle, seule la chirurgie est efficace",
                    "is_correct": False,
                    "feedback": "Non : la podologie agit bien par semelles orthopédiques avec objectif antalgique.",
                },
            ],
        },

        # ── Q10 — Les cors ───────────────────────────────────────────────────
        {
            "kind": "single",
            "topic": "Cors & Durillons",
            "text": (
                "Quelle est la principale cause de formation d'un cor ?"
            ),
            "choices": [
                {
                    "id": "A",
                    "label": "Une infection bactérienne de la peau",
                    "is_correct": False,
                    "feedback": "Non : les cors ne sont pas d'origine infectieuse mais mécanique.",
                },
                {
                    "id": "B",
                    "label": "Un frottement ou une pression répétée sur une zone localisée",
                    "is_correct": True,
                    "feedback": "Exact ! Le cor se forme en réponse à un frottement ou pression répétée, créant un noyau de kératose douloureux. (Fiche Les cors)",
                },
                {
                    "id": "C",
                    "label": "Un excès de vitamine D",
                    "is_correct": False,
                    "feedback": "Les vitamines n'ont aucun lien avec la formation des cors.",
                },
                {
                    "id": "D",
                    "label": "Une allergie au cuir de la chaussure",
                    "is_correct": False,
                    "feedback": "Une allergie peut irriter la peau, mais ne forme pas de cors.",
                },
            ],
        },

        # ── Q11 — Verrues ────────────────────────────────────────────────────
        {
            "kind": "multi",
            "topic": "Verrues",
            "text": (
                "Quels lieux ou comportements favorisent l'apparition de verrues plantaires ? "
                "(plusieurs réponses correctes)"
            ),
            "choices": [
                {
                    "id": "A",
                    "label": "La fréquentation de piscines",
                    "is_correct": True,
                    "feedback": "Oui ! La piscine est un lieu de contamination au papillomavirus sur peau humide et macérée.",
                },
                {
                    "id": "B",
                    "label": "Les vestiaires communs",
                    "is_correct": True,
                    "feedback": "Correct ! Les vestiaires partagés sont cités comme facteur favorisant la transmission.",
                },
                {
                    "id": "C",
                    "label": "Porter des chaussures en cuir",
                    "is_correct": False,
                    "feedback": "Le port de chaussures en cuir n'est pas un facteur favorisant les verrues.",
                },
                {
                    "id": "D",
                    "label": "Les salles de fitness",
                    "is_correct": True,
                    "feedback": "Oui ! Le fitness (sols partagés, pieds nus) favorise la transmission du papillomavirus.",
                },
            ],
        },

    ]  # fin questions_data

    for qd in questions_data:
        db.add(Question(
            quiz_id=quiz_id,
            kind=qd["kind"],
            topic=qd["topic"],
            text=qd["text"],
            choices_json=json.dumps(qd["choices"], ensure_ascii=False),
        ))
    db.commit()
