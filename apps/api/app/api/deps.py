import uuid

import jwt
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_access_token
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Identifiants invalides ou session expirée",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
        user_id = uuid.UUID(payload["sub"])
        tenant_id = uuid.UUID(payload["tid"])
    except (jwt.InvalidTokenError, ValueError):
        raise _CREDENTIALS_ERROR from None
    user = db.get(User, user_id)
    if user is None or user.tenant_id != tenant_id:
        raise _CREDENTIALS_ERROR
    return user


def get_tenant_id(x_tenant_id: uuid.UUID = Header(...)) -> uuid.UUID:
    """Temporaire : le tenant vient d'un header. Remplacé par le JWT à la tâche M1-3."""
    return x_tenant_id


def get_queue(request: Request):
    return getattr(request.app.state, "queue", None)
