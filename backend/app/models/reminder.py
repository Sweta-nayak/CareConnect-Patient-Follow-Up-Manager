
import uuid

from datetime import datetime

from sqlalchemy import (
    String,
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


class Reminder(Base):

    __tablename__ = "reminders"

    # Primary Key
    reminder_id: Mapped[str] = mapped_column(
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

    # Care Instruction ID
    instruction_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True
    )

    # Appointment ID
    appointment_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True
    )

    # Notification Channel
    channel: Mapped[str] = mapped_column(
        Enum(
            "SMS",
            "WHATSAPP",
            name="reminder_channel"
        ),
        nullable=False
    )

    # Reminder Type
    reminder_type: Mapped[str] = mapped_column(
        Enum(
            "APPOINTMENT",
            "MEDICINE",
            "TEST",
            "CONSULTATION",
            name="reminder_type"
        ),
        nullable=False
    )

    # Scheduled Date and Time
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    # Reminder Message
    message_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Reminder Status
    status: Mapped[str] = mapped_column(
        Enum(
            "PENDING",
            "SIMULATED",
            "SENT",
            "FAILED",
            "CANCELLED",
            name="reminder_status"
        ),
        default="PENDING",
        server_default=text("'PENDING'")
    )

    # Duplicate Prevention Key
    idempotency_key: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    # Attempted Date and Time
    attempted_at: Mapped[datetime | None] = mapped_column(
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
            "idempotency_key",
            name="uq_reminder_idempotency"
        ),

        ForeignKeyConstraint(
            ["organization_id", "patient_id"],
            ["patients.organization_id", "patients.patient_id"],
            name="fk_reminder_patient"
        ),

        ForeignKeyConstraint(
            ["organization_id", "instruction_id"],
            [
                "care_instructions.organization_id",
                "care_instructions.instruction_id"
            ],
            name="fk_reminder_instruction"
        ),

        ForeignKeyConstraint(
            ["organization_id", "appointment_id"],
            [
                "appointments.organization_id",
                "appointments.appointment_id"
            ],
            name="fk_reminder_appointment"
        ),

        Index(
            "idx_reminder_schedule",
            "organization_id",
            "scheduled_at",
            "status"
        )
    )
