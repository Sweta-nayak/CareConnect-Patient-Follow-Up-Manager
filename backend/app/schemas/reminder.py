
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ReminderChannel = Literal["SMS", "WHATSAPP"]

ReminderType = Literal[
    "APPOINTMENT",
    "MEDICINE",
    "TEST",
    "CONSULTATION"
]

ReminderStatus = Literal[
    "PENDING",
    "SIMULATED",
    "SENT",
    "FAILED",
    "CANCELLED"
]


class ReminderCreate(BaseModel):

    patient_id: str

    instruction_id: str | None = None

    appointment_id: str | None = None

    channel: ReminderChannel

    reminder_type: ReminderType

    scheduled_at: datetime

    message_text: str = Field(
        min_length=1,
        max_length=5000
    )

    idempotency_key: str = Field(
        min_length=1,
        max_length=150
    )

    @model_validator(mode="after")
    def validate_reference(self):

        if self.reminder_type == "APPOINTMENT":

            if not self.appointment_id:
                raise ValueError(
                    "Appointment ID is required for appointment reminders"
                )

            if self.instruction_id:
                raise ValueError(
                    "Appointment reminders cannot have a care instruction ID"
                )

        else:

            if not self.instruction_id:
                raise ValueError(
                    "Care instruction ID is required for this reminder type"
                )

            if self.appointment_id:
                raise ValueError(
                    "Care instruction reminders cannot have an appointment ID"
                )

        return self


class ReminderResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    reminder_id: str

    organization_id: str

    patient_id: str

    instruction_id: str | None

    appointment_id: str | None

    channel: ReminderChannel

    reminder_type: ReminderType

    scheduled_at: datetime

    message_text: str

    status: ReminderStatus

    idempotency_key: str

    attempted_at: datetime | None

    created_at: datetime
