import uuid

from fastapi import Header, Request


def get_tenant_id(x_tenant_id: uuid.UUID = Header(...)) -> uuid.UUID:
    """Temporaire : le tenant vient d'un header. À remplacer par le JWT après l'auth."""
    return x_tenant_id


def get_queue(request: Request):
    return getattr(request.app.state, "queue", None)
