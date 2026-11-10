import enum
import uuid
from datetime import date

from sqlalchemy import JSON, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdTimestampMixin, TenantMixin, str_enum


class CandidateStatus(enum.StrEnum):
    NEW = "new"  # message reçu, pas encore analysé
    SCREENED = "screened"  # infos extraites par l'IA
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    HIRED = "hired"  # converti en Agent


class Candidate(IdTimestampMixin, TenantMixin, Base):
    """Candidat arrivé via WhatsApp (texte ou note vocale)."""

    __tablename__ = "candidates"
    __table_args__ = (UniqueConstraint("tenant_id", "phone"),)
    phone: Mapped[str] = mapped_column(String(32), index=True)
    full_name: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(100))
    raw_messages: Mapped[str | None] = mapped_column(Text)  # transcriptions concaténées
    extracted: Mapped[dict | None] = mapped_column(JSON)  # sortie structurée de l'IA
    score: Mapped[int | None] = mapped_column(Integer)  # 0-100
    status: Mapped[CandidateStatus] = mapped_column(
        str_enum(CandidateStatus), default=CandidateStatus.NEW
    )


class AgentStatus(enum.StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Agent(IdTimestampMixin, TenantMixin, Base):
    """Agent de sécurité employé par le tenant."""

    __tablename__ = "agents"
    __table_args__ = (UniqueConstraint("tenant_id", "phone"),)
    candidate_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("candidates.id"))
    full_name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str] = mapped_column(String(32), index=True)
    city: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[AgentStatus] = mapped_column(str_enum(AgentStatus), default=AgentStatus.ACTIVE)


class DocumentType(enum.StrEnum):
    CIN = "cin"
    CRIMINAL_RECORD = "criminal_record"  # fiche anthropométrique / casier
    PRO_CARD = "pro_card"  # carte professionnelle
    CONTRACT = "contract"
    OTHER = "other"


class AgentDocument(IdTimestampMixin, TenantMixin, Base):
    """Document d'un agent, avec date d'expiration pour les alertes."""

    __tablename__ = "agent_documents"
    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"))
    type: Mapped[DocumentType] = mapped_column(str_enum(DocumentType))
    storage_key: Mapped[str] = mapped_column(String(500))  # clé S3/MinIO, jamais le fichier en BDD
    expires_on: Mapped[date | None] = mapped_column(Date)
