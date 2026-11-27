
import uuid

from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    JSON,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    text
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    # Primary Key
    audit_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Organization ID
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.organization_id"),
        nullable=False
    )

    # User who performed the action
    actor_user_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True
    )

    # Action performed
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Entity Type
    entity_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # Entity ID
    entity_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True
    )

    # Additional Details
    details: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    # Created Date
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    # Database Constraints
    __table_args__ = (

        ForeignKeyConstraint(
            ["organization_id", "actor_user_id"],
            ["users.organization_id", "users.user_id"],
            name="fk_audit_user"
        ),

        Index(
            "idx_audit_org_date",
            "organization_id",
            "created_at"
        )
    )
