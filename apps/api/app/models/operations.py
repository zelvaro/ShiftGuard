import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdTimestampMixin, TenantMixin


class Site(IdTimestampMixin, TenantMixin, Base):
    """Site client à sécuriser (résidence, usine, stade, événement...)."""

    __tablename__ = "sites"
    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(String(300))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    geofence_radius_m: Mapped[int] = mapped_column(Integer, default=150)
    qr_secret: Mapped[str | None] = mapped_column(String(64))  # pour générer le QR de pointage


class ShiftStatus(enum.StrEnum):
    OPEN = "open"  # pas encore d'agent
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    MISSED = "missed"


class Shift(IdTimestampMixin, TenantMixin, Base):
    __tablename__ = "shifts"
    site_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"))
    agent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("agents.id"))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[ShiftStatus] = mapped_column(Enum(ShiftStatus), default=ShiftStatus.OPEN)


class CheckMethod(enum.StrEnum):
    QR = "qr"
    GPS = "gps"
    MANUAL = "manual"


class Attendance(IdTimestampMixin, TenantMixin, Base):
    """Pointage d'un agent sur un shift."""

    __tablename__ = "attendances"
    shift_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("shifts.id", ondelete="CASCADE"))
    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"))
    check_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    check_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    method: Mapped[CheckMethod] = mapped_column(Enum(CheckMethod))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
