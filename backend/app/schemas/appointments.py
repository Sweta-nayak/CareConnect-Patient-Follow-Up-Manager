
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


AppointmentStatus = Literal[
    "SCHEDULED",
    "CONFIRMED",
    "ATTENDED",
    "MISSED",
    "RESCHEDULED",
    "CANCELLED"
]


class AppointmentCreate(BaseModel):
    patient_id: str
    clinician_user_id: str
    appointment_datetime: datetime

    appointment_type: str | None = Field(
        default=None,
        max_length=50
    )

    reason: str | None = Field(
        default=None,
        max_length=255
    )

    notes: str | None = None


class AppointmentUpdate(BaseModel):
    patient_id: str | None = None
    clinician_user_id: str | None = None
    appointment_datetime: datetime | None = None
    appointment_type: str | None = Field(
        default=None,
        max_length=50
    )
    status: AppointmentStatus | None = None
    reason: str | None = Field(
        default=None,
        max_length=255
    )
    notes: str | None = None


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    appointment_id: str
    patient_id: str
    clinician_user_id: str
    appointment_datetime: datetime
    appointment_type: str | None
    status: str
    reason: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
