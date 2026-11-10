"""Client minimal pour la WhatsApp Cloud API (Meta)."""

import httpx

from app.core.config import get_settings

GRAPH_URL = "https://graph.facebook.com"


async def send_text(to: str, body: str) -> dict:
    s = get_settings()
    url = f"{GRAPH_URL}/{s.whatsapp_api_version}/{s.whatsapp_phone_number_id}/messages"
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            url, json=payload, headers={"Authorization": f"Bearer {s.whatsapp_access_token}"}
        )
        r.raise_for_status()
        return r.json()


async def download_media(media_id: str) -> bytes:
    """Récupère un fichier (note vocale, photo de CIN...) envoyé par l'utilisateur."""
    s = get_settings()
    headers = {"Authorization": f"Bearer {s.whatsapp_access_token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        meta = await client.get(f"{GRAPH_URL}/{s.whatsapp_api_version}/{media_id}", headers=headers)
        meta.raise_for_status()
        media = await client.get(meta.json()["url"], headers=headers)
        media.raise_for_status()
        return media.content


def parse_incoming(payload: dict) -> list[dict]:
    """Aplatit le webhook Meta en une liste de messages simples."""
    messages = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            phone_number_id = value.get("metadata", {}).get("phone_number_id")
            for m in value.get("messages", []):
                messages.append(
                    {
                        "phone_number_id": phone_number_id,
                        "from": m.get("from"),
                        "id": m.get("id"),
                        "type": m.get("type"),
                        "text": m.get("text", {}).get("body"),
                        "media_id": (m.get(m.get("type"), {}) or {}).get("id")
                        if m.get("type") in {"audio", "image", "document"}
                        else None,
                    }
                )
    return messages
