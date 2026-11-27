
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


InstructionType = Literal[
    "MEDICINE",
    "TEST",
    "CONSULTATION"
]

ApprovalStatus = Literal[
    "DRAFT",
    "APPROVED",
    "CANCELLED"
]


# =========================================
# 1. CREATE CARE INSTRUCTION
# =========================================

class CareInstructionCreate(BaseModel):

    patient_id: str

    clinician_user_id: str

    instruction_type: InstructionType

    instruction_text: str = Field(
        min_length=3
    )

    start_date: date | None = None

    end_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self):

        if (
            self.start_date
            and self.end_date
            and self.end_date < self.start_date
        ):
            raise ValueError(
                "End date cannot be earlier than start date"
            )

        return self


# =========================================
# 2. UPDATE CARE INSTRUCTION
# =========================================

class CareInstructionUpdate(BaseModel):

    instruction_type: InstructionType | None = None

    instruction_text: str | None = Field(
        default=None,
        min_length=3
    )

    start_date: date | None = None

    end_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self):

        if (
            self.start_date
            and self.end_date
            and self.end_date < self.start_date
        ):
            raise ValueError(
                "End date cannot be earlier than start date"
            )

        return self


# =========================================
# 3. CARE INSTRUCTION RESPONSE
# =========================================

class CareInstructionResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    instruction_id: str

    organization_id: str

    patient_id: str

    clinician_user_id: str

    instruction_type: str

    instruction_text: str

    start_date: date | None

    end_date: date | None

    approval_status: str

    approved_at: datetime | None

    created_at: datetime
