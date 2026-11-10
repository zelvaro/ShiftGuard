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
                                 │  Redis  +  arq   │─────▶│ IA : Whisper │
                                 │  (worker)        │      │      + LLM   │
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
| `candidates` | Candidats WhatsApp : messages, extraction IA, score, statut |
| `agents` | Agents employés (issus d'un candidat ou créés à la main) |
| `agent_documents` | CIN, casier, carte pro… avec date d'expiration |
| `sites` | Sites clients, coordonnées GPS, rayon de geofence, secret QR |
| `shifts` | Créneaux site × horaire × agent, statut |
| `attendances` | Pointages (méthode QR / GPS / manuel, position) |

Toutes les tables métier portent un `tenant_id`.

## Flux 1 — Candidature WhatsApp

1. Le candidat écrit ou envoie un vocal au numéro de la société.
2. Meta appelle `POST /api/v1/webhooks/whatsapp` → l'API répond 200 tout de suite et met le message en file.
3. Le worker (`process_incoming_message`) :
   - retrouve le tenant via `phone_number_id`, puis le candidat via son numéro (ou le crée) ;
   - si audio : télécharge le média → transcription Whisper ;
   - concatène les messages → LLM → `CandidateExtraction` (JSON validé) ;
   - calcule le score, met à jour le statut ;
   - pose la question manquante suivante au candidat (ville, carte pro, disponibilité…).
4. Le RH voit les candidats triés par score dans le back-office.

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
