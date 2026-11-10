from fastapi import APIRouter

from app.api.v1.routes import candidates, health, shifts, whatsapp

api_router = APIRouter(prefix="/api/v1")
for r in (health.router, candidates.router, shifts.router, whatsapp.router):
    api_router.include_router(r)
