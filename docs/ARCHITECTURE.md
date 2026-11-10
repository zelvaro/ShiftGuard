# Architecture

## Vue d'ensemble

```
 Candidats / Agents                      RH / Planificateurs
     (WhatsApp)                             (navigateur)
         │                                       │
         ▼                                       ▼
 ┌────────────────┐   webhook   ┌────────────────────────┐
 │ WhatsApp Cloud │────────────▶│      API FastAPI       │◀──── Next.js (apps/web)
 │   API (Meta)   │◀────────────│  /api/v1/...           │
 └────────────────┘  messages   └──────────┬─────────────┘
                                           │ enqueue
                                           ▼
                                 ┌──────────────────┐      ┌──────────────┐
                                 │  Redis  +  arq   │ ···▶ │ IA (V2) :    │
                                 │  (worker)        │      │ Whisper + LLM│
                                 └────────┬─────────┘      └──────────────┘
                                          │
                         ┌────────────────┴───────────────┐
                         ▼                                ▼
                 ┌──────────────┐                 ┌──────────────┐
                 │  PostgreSQL  │                 │ S3 / MinIO   │
                 └──────────────┘                 │ (documents)  │
                                                  └──────────────┘
```

## Modèle de données

| Table | Rôle |
|---|---|
| `tenants` | Société cliente |
| `users` | Utilisateurs back-office (admin, planner, supervisor) |
| `candidates` | Candidats WhatsApp : réponses au questionnaire, étape de conversation, score, statut |
| `agents` | Agents employés (issus d'un candidat ou créés à la main) |
| `agent_documents` | CIN, casier, carte pro… avec date d'expiration |
| `sites` | Sites clients, coordonnées GPS, rayon de geofence, secret QR |
| `shifts` | Créneaux site × horaire × agent, statut |
| `attendances` | Pointages (méthode QR / GPS / manuel, position) |

Toutes les tables métier portent un `tenant_id`.

## Flux 1 — Candidature WhatsApp (V1 : questions guidées)

1. Le candidat écrit au numéro de la société.
2. Meta appelle `POST /api/v1/webhooks/whatsapp` → l'API vérifie la signature, répond 200 tout de suite et met le message en file.
3. Le worker (`process_incoming_message`) :
   - ignore le message s'il a déjà été traité (idempotence par `message.id`) ;
   - retrouve le tenant via `phone_number_id`, puis le candidat via son numéro (ou le crée) ;
   - lit l'étape de conversation du candidat et enregistre la réponse reçue (bouton, liste ou texte court) ;
   - envoie la question suivante en message interactif :

     | Étape | Question | Format |
     |---|---|---|
     | 1 | Nom complet | texte |
     | 2 | Ville | liste |
     | 3 | Carte professionnelle ? | boutons oui / non |
     | 4 | Années d'expérience | liste (0, 1-2, 3-5, 5+) |
     | 5 | Disponibilité | liste (jour, nuit, week-end, immédiate) |

   - à la dernière étape : calcul du score par règles, statut `screened`, message de confirmation.
4. Si le candidat envoie un vocal, une image ou un fichier : le média est stocké (MinIO) et rattaché au candidat pour que le RH puisse l'écouter, puis le bot répète la question en cours.
5. Le RH voit les candidats triés par score dans le back-office.

En V2, un vocal sera transcrit puis analysé par un LLM pour pré-remplir les réponses ; le bot ne posera plus que les questions restées sans réponse (voir `PLAN.md` §3).

## Flux 2 — Remplacement

1. Un shift passe à `open` (absence signalée, agent retiré).
2. Le système sélectionne les agents disponibles (pas d'autre shift qui chevauche, même ville, documents valides).
3. Envoi d'un template WhatsApp « Shift disponible demain 20h–8h à X, répondre OUI ».
4. Premier « OUI » → affectation → confirmation aux autres.

## Flux 3 — Pointage

1. Chaque site a un QR code (signé avec `qr_secret`) affiché sur place.
2. L'agent scanne → page web mobile → envoi du QR + position GPS.
3. L'API vérifie : bon site, bon shift, position dans la geofence → `attendance` créée.

## Sécurité (à faire avant la prod)

- Vérification de la signature `X-Hub-Signature-256` des webhooks Meta.
- Auth JWT ; le `tenant_id` vient du token, jamais du client (le header `X-Tenant-ID` actuel est provisoire).
- Documents chiffrés au repos, URLs de téléchargement signées et courtes.
- Journal d'accès aux données sensibles.
