# Proposition de stack

Principe : une stack que l'on maîtrise, rapide à livrer, et où l'IA est un citoyen de première classe.

## Back-end — FastAPI (Python 3.12)

- **Pourquoi** : l'essentiel de la valeur est dans l'IA (transcription, extraction, scoring) ; tout l'écosystème IA est en Python. Un seul langage côté serveur.
- FastAPI : typage Pydantic, doc OpenAPI auto (`/docs`), async natif pour les appels WhatsApp/LLM.
- **SQLAlchemy 2** (ORM typé) + **Alembic** (migrations).
- Alternative écartée : NestJS — bon choix, mais deux langages pour un dev solo.

## Base de données — PostgreSQL

- Données très relationnelles (tenant → sites → shifts → pointages → agents).
- Multi-tenant **par colonne `tenant_id`** : le plus simple pour démarrer. Évolution possible vers le Row-Level Security de Postgres.
- `JSON` pour la sortie brute de l'IA sur les candidats.

## File de tâches — Redis + arq

- Meta exige une réponse rapide au webhook : le traitement (téléchargement du vocal, transcription, LLM) part en tâche de fond.
- **arq** : léger, async, suffisant pour le MVP. Celery serait plus lourd sans gain ici.
- Sert aussi aux crons (alertes d'expiration, rappels de shift).

## Front-end — Next.js 16 + TypeScript + Tailwind

- Back-office web (RH, planificateurs) ; déjà utilisé sur d'autres projets.
- Ajouter **shadcn/ui** pour les composants (tables, formulaires, calendrier) et **TanStack Query** pour les appels API.
- Côté agents : pas d'app à installer au début. Tout passe par **WhatsApp** + une page web mobile pour le pointage (scan QR / GPS).

## WhatsApp — Cloud API officielle (Meta)

- Seule option fiable et autorisée (les librairies non officielles font bannir les numéros).
- Gratuit à l'entrée, facturation par conversation ensuite. Un numéro par tenant (ou un numéro ShiftGuard partagé au début).
- Messages sortants hors fenêtre de 24 h = **templates** à faire valider par Meta (ex. proposition de remplacement).

## IA

| Besoin | Choix | Note |
|---|---|---|
| Transcription vocale | Whisper (`whisper-large-v3`) via Groq ou OpenAI | À tester tôt sur de vrais vocaux en darija |
| Extraction du profil | LLM avec sortie JSON validée par Pydantic | Prompt + schéma `CandidateExtraction` |
| Scoring | Règles simples et explicables d'abord | Le LLM extrait, le code note : plus prévisible |

Le fournisseur est isolé derrière `app/services/ai/` pour pouvoir en changer sans toucher au reste.

## Stockage — S3-compatible

- MinIO en local, n'importe quel S3 en prod. Les fichiers ne vont jamais en base, seulement leur clé.

## Hébergement (à décider plus tard)

- Démarrage : un VPS (Docker Compose) ou Railway/Render pour l'API, Vercel pour le front.
- À vérifier avec les premiers clients : exigence d'hébergement au Maroc pour des données de type CIN/casier.

## Qualité

- `pytest` + `ruff` côté API, ESLint côté web.
- CI GitHub Actions à ajouter dès les premières fonctionnalités.
