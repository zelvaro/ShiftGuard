import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdTimestampMixin, TenantMixin


class Tenant(IdTimestampMixin, Base):
    """Société cliente (société de gardiennage, agence d'intérim...)."""

    __tablename__ = "tenants"
    name: Mapped[str] = mapped_column(String(200))
    whatsapp_phone_number_id: Mapped[str | None] = mapped_column(String(64), unique=True)


class UserRole(enum.StrEnum):
    ADMIN = "admin"
    PLANNER = "planner"
    SUPERVISOR = "supervisor"


class User(IdTimestampMixin, TenantMixin, Base):
    """Utilisateur back-office (RH, planificateur, chef de site)."""

    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True)
    full_name: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.PLANNER)
