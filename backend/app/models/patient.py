
import uuid

from datetime import date, datetime

from sqlalchemy import (
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    UniqueConstraint,
    text
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Patient(Base):

    __tablename__ = "patients"

    # Primary Key
    patient_id: Mapped[str] = mapped_column(
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

    # Patient Name
    patient_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Date of Birth
    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    # Gender
    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Phone Number
    phone_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    # Email
    email: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    # SMS Consent
    consent_sms: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("0")
    )

    # WhatsApp Consent
    consent_whatsapp: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("0")
    )

    # Active Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("1")
    )

    # Created By
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True
    )

    # Creation Date
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    # Composite foreign key and unique constraint
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "created_by"],
            ["users.organization_id", "users.user_id"],
            name="fk_patients_creator"
        ),

        UniqueConstraint(
            "organization_id",
            "patient_id",
            name="uq_patient_org_id"
        ),
    )
