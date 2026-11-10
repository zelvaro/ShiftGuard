from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Tenant, User
from app.models.tenant import UserRole
from app.schemas.auth import SignupRequest, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_for(user: User) -> TokenOut:
    return TokenOut(access_token=create_access_token(user.id, user.tenant_id, user.role.value))


@router.post("/signup", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def signup(data: SignupRequest, db: Session = Depends(get_db)) -> TokenOut:
    """Crée une société cliente et son premier utilisateur (admin)."""
    email = data.email.lower()
    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email déjà utilisé")

    tenant = Tenant(name=data.company_name.strip())
    db.add(tenant)
    db.flush()
    user = User(
        tenant_id=tenant.id,
        email=email,
        full_name=data.full_name.strip(),
        password_hash=hash_password(data.password),
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    return _token_for(user)


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenOut:
    """Connexion par email (champ `username`) et mot de passe."""
    user = db.scalar(select(User).where(User.email == form.username.lower()))
    if not verify_password(form.password, user.password_hash if user else None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _token_for(user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user
