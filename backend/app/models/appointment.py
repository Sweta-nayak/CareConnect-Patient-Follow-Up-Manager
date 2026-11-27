
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
    text,
    FetchedValue
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Appointment(Base):

    __tablename__ = "appointments"

    # Primary Key
    appointment_id: Mapped[str] = mapped_column(
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

    # Assigned Doctor
    clinician_user_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False
    )

    # Appointment Date and Time
    appointment_datetime: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    # Appointment Type
    appointment_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Appointment Status
    status: Mapped[str] = mapped_column(
        Enum(
            "SCHEDULED",
            "CONFIRMED",
            "ATTENDED",
            "MISSED",
            "RESCHEDULED",
            "CANCELLED",
            name="appointment_status"
        ),
        default="SCHEDULED",
        server_default=text("'SCHEDULED'")
    )

    # Reason
    reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # Additional Notes
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Created By
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True
    )

    # Created Date
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    # Updated Date
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue()
    )

    # Constraints and Indexes
    __table_args__ = (

        UniqueConstraint(
            "organization_id",
            "appointment_id",
            name="uq_appointment_org_id"
        ),

        ForeignKeyConstraint(
            ["organization_id", "patient_id"],
            ["patients.organization_id", "patients.patient_id"],
            name="fk_appointment_patient"
        ),

        ForeignKeyConstraint(
            ["organization_id", "clinician_user_id"],
            ["users.organization_id", "users.user_id"],
            name="fk_appointment_clinician"
        ),

        ForeignKeyConstraint(
            ["organization_id", "created_by"],
            ["users.organization_id", "users.user_id"],
            name="fk_appointment_creator"
        ),

        Index(
            "idx_appointment_schedule",
            "organization_id",
            "appointment_datetime"
        ),

        Index(
            "idx_appointment_status",
            "organization_id",
            "status"
        )
    )
