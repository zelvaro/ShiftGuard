"""Tâches asynchrones (arq + Redis) : traitement des messages WhatsApp, alertes."""

from arq.connections import RedisSettings

from app.core.config import get_settings


async def process_incoming_message(ctx: dict, message: dict) -> None:
    """1. retrouver/créer le candidat  2. transcrire si audio  3. extraire + scorer  4. répondre."""
    # TODO : implémenter le pipeline (voir docs/ARCHITECTURE.md)


async def check_expiring_documents(ctx: dict) -> None:
    """Cron quotidien : alerter sur les documents qui expirent dans les 30 jours."""
    # TODO


class WorkerSettings:
    functions = [process_incoming_message, check_expiring_documents]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
