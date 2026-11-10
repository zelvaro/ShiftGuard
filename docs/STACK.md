# Proposition de stack

Principe : une stack que l'on maîtrise, rapide à livrer, et prête à accueillir l'IA en V2 sans refonte.

## Back-end — FastAPI (Python 3.12)

- **Pourquoi** : la V2 ajoutera l'IA (transcription, extraction) et tout l'écosystème IA est en Python. Un seul langage côté serveur dès la V1.
- FastAPI : typage Pydantic, doc OpenAPI auto (`/docs`), async natif pour les appels WhatsApp/LLM.
- **SQLAlchemy 2** (ORM typé) + **Alembic** (migrations).
- Alternative écartée : NestJS — bon choix, mais deux langages pour un dev solo.

## Base de données — PostgreSQL

- Données très relationnelles (tenant → sites → shifts → pointages → agents).
- Multi-tenant **par colonne `tenant_id`** : le plus simple pour démarrer. Évolution possible vers le Row-Level Security de Postgres.
- `JSON` pour les réponses au questionnaire (et, en V2, la sortie brute de l'IA).

## File de tâches — Redis + arq

- Meta exige une réponse rapide au webhook : le traitement (enregistrement de la réponse, envoi de la question suivante, stockage des médias) part en tâche de fond.
- **arq** : léger, async, suffisant pour le MVP. Celery serait plus lourd sans gain ici.
- Sert aussi aux crons (alertes d'expiration, rappels de shift).

## Front-end — Next.js 16 + TypeScript + Tailwind

- Back-office web (RH, planificateurs) ; déjà utilisé sur d'autres projets.
- Ajouter **shadcn/ui** pour les composants (tables, formulaires, calendrier) et **TanStack Query** pour les appels API.
- Côté agents : pas d'app à installer au début. Tout passe par **WhatsApp** + une page web mobile pour le pointage (scan QR / GPS).

## WhatsApp — Cloud API officielle (Meta)

- Seule option fiable et autorisée (les librairies non officielles font bannir les numéros).
- Messages interactifs (boutons jusqu'à 3 choix, listes jusqu'à 10) : la base du questionnaire candidat.
- Gratuit à l'entrée, facturation par conversation ensuite. Un numéro par tenant (ou un numéro ShiftGuard partagé au début).
- Messages sortants hors fenêtre de 24 h = **templates** à faire valider par Meta (ex. proposition de remplacement).

## Qualification des candidats

**V1 — sans IA** : questions guidées par messages interactifs WhatsApp (boutons et listes). Les réponses remplissent directement le profil, le score est calculé par des règles explicables (`score_candidate`). Rien à entraîner ni à payer, et fiable dès le premier jour.

**V2 — vocal et IA**, une fois des vocaux réels collectés pendant le pilote :

| Besoin | Choix | Note |
|---|---|---|
| Transcription vocale | Whisper (`whisper-large-v3`) via Groq ou OpenAI | À évaluer sur de vrais vocaux en darija |
| Extraction du profil | LLM avec sortie JSON validée par Pydantic | Prompt + schéma `CandidateExtraction` |
| Scoring | Mêmes règles qu'en V1 | Le LLM extrait, le code note : plus prévisible |

Le code V2 est déjà isolé dans `app/services/ai/` (fonctions vides pour l'instant).

## Stockage — S3-compatible

- MinIO en local, n'importe quel S3 en prod. Les fichiers ne vont jamais en base, seulement leur clé.

## Hébergement (à décider plus tard)

- Démarrage : un VPS (Docker Compose) ou Railway/Render pour l'API, Vercel pour le front.
- À vérifier avec les premiers clients : exigence d'hébergement au Maroc pour des données de type CIN/casier.

## Qualité

- `pytest` + `ruff` côté API, ESLint côté web.
- CI GitHub Actions à ajouter dès les premières fonctionnalités.
