import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.api.deps import get_queue
from app.core.config import get_settings
from app.services.whatsapp import parse_incoming

router = APIRouter(prefix="/webhooks/whatsapp", tags=["whatsapp"])
log = logging.getLogger(__name__)


@router.get("", response_class=PlainTextResponse)
def verify(
    mode: str = Query(alias="hub.mode"),
    token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge"),
) -> str:
    """Vérification du webhook demandée par Meta lors de la configuration."""
    if mode == "subscribe" and token == get_settings().whatsapp_verify_token:
        return challenge
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("")
async def receive(request: Request, queue=Depends(get_queue)) -> dict:
    """Répondre vite (200) à Meta ; le traitement lourd part dans le worker."""
    # TODO : vérifier la signature X-Hub-Signature-256 avec l'app secret.
    messages = parse_incoming(await request.json())
    for m in messages:
        if queue is not None:
            await queue.enqueue_job("process_incoming_message", m)
        else:
            log.warning("Queue indisponible, message ignoré: %s", m.get("id"))
    return {"received": len(messages)}
