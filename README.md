# ShiftGuard

**Recrutement, planning et pointage des agents de sécurité — piloté par WhatsApp.**

ShiftGuard est un SaaS B2B pour les sociétés de gardiennage et d'intérim au Maroc. Il remplace les tableaux Excel, les groupes WhatsApp et les appels de dernière minute par un outil unique, pensé pour des centaines d'agents répartis sur plusieurs sites.

> Objectif : un MVP utilisé par de premières sociétés clientes bien avant le Mondial 2030.

## Le problème

- Les candidats postulent par WhatsApp, en messages épars ou en notes vocales : impossible à trier à la main en volume.
- Le planning des shifts vit dans Excel ; une absence = des dizaines d'appels pour trouver un remplaçant.
- Le pointage sur site est déclaratif et difficile à vérifier.
- Les documents obligatoires (CIN, casier, carte professionnelle) expirent sans que personne ne le voie.

## Fonctionnalités du MVP

| Module | Ce qu'il fait |
|---|---|
| **Recrutement WhatsApp** | Le candidat répond à des questions guidées (boutons, listes) → profil rempli → score → shortlist dans le back-office. Les vocaux reçus sont gardés pour écoute par le RH |
| **Planning** | Sites, shifts, affectation des agents, vue semaine |
| **Remplacements** | Shift sans agent → l'outil propose et contacte des agents disponibles par WhatsApp |
| **Pointage** | Check-in / check-out par QR code du site ou géolocalisation (geofence) |
| **Documents** | Stockage des pièces, alertes avant expiration |

Hors MVP : vocal et IA (V2), paie à la mission, facturation clients, application mobile native, tarification.

## Stack

| Couche | Choix |
|---|---|
| Back-end | Python 3.12, **FastAPI**, SQLAlchemy 2, Alembic |
| Base de données | **PostgreSQL** (multi-tenant par `tenant_id`) |
| Tâches asynchrones | **Redis + arq** (traitement des messages, crons d'alertes) |
| Front-end | **Next.js 16**, React 19, TypeScript, Tailwind CSS 4 |
| Messagerie | **WhatsApp Cloud API** (Meta, officielle) |
| IA (V2) | Whisper (transcription darija/FR/AR) + LLM pour l'extraction structurée, fournisseur interchangeable |
| Stockage fichiers | S3-compatible (MinIO en local) |
| Dev | Docker Compose, pytest, ruff, ESLint |

Détails et justifications : [`docs/STACK.md`](docs/STACK.md) · Architecture : [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) · Plan : [`docs/PLAN.md`](docs/PLAN.md)

## Structure du dépôt

```
ShiftGuard/
├── apps/
│   ├── api/                 # FastAPI
│   │   ├── app/
│   │   │   ├── api/v1/      # routes : health, candidates, shifts, webhooks WhatsApp
│   │   │   ├── core/        # config, base de données
│   │   │   ├── models/      # tenants, workforce (candidats, agents, documents), operations (sites, shifts, pointages)
│   │   │   ├── schemas/     # modèles Pydantic
│   │   │   ├── services/    # client WhatsApp, scoring, IA (V2 : transcription, extraction)
│   │   │   └── workers/     # tâches arq
│   │   ├── migrations/      # Alembic
│   │   └── tests/
│   └── web/                 # Next.js (back-office)
├── docs/
├── docker-compose.yml       # Postgres, Redis, MinIO (+ api/worker avec --profile full)
└── .env.example
```

## Démarrage en local

Prérequis : Docker Desktop, Python 3.12+, Node.js 20+.

```bash
# 1. Variables d'environnement
cp .env.example .env

# 2. Infra (Postgres, Redis, MinIO)
docker compose up -d

# 3. API
cd apps/api
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS : source .venv/bin/activate)
pip install -e ".[dev]"
alembic revision --autogenerate -m "init"
alembic upgrade head
uvicorn app.main:app --reload    # http://localhost:8000/docs

# 4. Worker (autre terminal, même venv)
arq app.workers.tasks.WorkerSettings

# 5. Front-end
cd apps/web
npm install
npm run dev                      # http://localhost:3000
```

Tout lancer dans Docker : `docker compose --profile full up -d --build`.

Tests et lint de l'API : `pytest` et `ruff check .` depuis `apps/api`.

## Roadmap

- [x] Squelette monorepo, modèle de données, webhook WhatsApp
- [ ] Authentification (JWT) et gestion des tenants / utilisateurs
- [ ] Recrutement WhatsApp guidé : questions à étapes → profil → scoring
- [ ] Back-office : liste des candidats, sites, planning semaine
- [ ] Pointage QR / GPS
- [ ] Remplacements automatiques
- [ ] Alertes d'expiration des documents
- [ ] Pilote avec 2–3 sociétés de gardiennage
- [ ] V2 : vocal (transcription + extraction IA)

## Conformité

ShiftGuard traite des données personnelles sensibles (CIN, casier judiciaire, géolocalisation). Avant toute mise en production : déclaration auprès de la **CNDP** (loi 09-08), consentement explicite des candidats, chiffrement des documents et hébergement à valider avec les clients.

## Licence

Propriétaire — tous droits réservés.
