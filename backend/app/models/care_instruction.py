
import uuid

from datetime import date, datetime

from sqlalchemy import (
    String,
    Date,
    DateTime,
    Enum,
    Text,
    ForeignKeyConstraint,
    UniqueConstraint,
    Index,
    text
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CareInstruction(Base):

    __tablename__ = "care_instructions"

    # Primary Key
    instruction_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Organization ID
    organization_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False
    )

    # Patient ID
    patient_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False
    )

    # Clinician ID
    clinician_user_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False
    )

    # Instruction Type
    instruction_type: Mapped[str] = mapped_column(
        Enum(
            "MEDICINE",
            "TEST",
            "CONSULTATION",
            name="instruction_type"
        ),
        nullable=False
    )

    # Instruction Details
    instruction_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Start Date
    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    # End Date
    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    # Approval Status
    approval_status: Mapped[str] = mapped_column(
        Enum(
            "DRAFT",
            "APPROVED",
            "CANCELLED",
            name="instruction_approval_status"
        ),
        default="DRAFT",
        server_default=text("'DRAFT'")
    )

    # Approval Date
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # Created Date
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    # Database Constraints
    __table_args__ = (

        UniqueConstraint(
            "organization_id",
            "instruction_id",
            name="uq_instruction_org_id"
        ),

        ForeignKeyConstraint(
            ["organization_id", "patient_id"],
            ["patients.organization_id", "patients.patient_id"],
            name="fk_instruction_patient"
        ),

        ForeignKeyConstraint(
            ["organization_id", "clinician_user_id"],
            ["users.organization_id", "users.user_id"],
            name="fk_instruction_clinician"
        ),

        Index(
            "idx_instruction_patient",
            "organization_id",
            "patient_id"
        )
    )
