
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# Used when creating a new patient
class PatientCreate(BaseModel):

    patient_name: str = Field(
        min_length=2,
        max_length=100
    )

    date_of_birth: date | None = None

    gender: str | None = Field(
        default=None,
        max_length=20
    )

    phone_number: str = Field(
        min_length=10,
        max_length=20
    )

    email: EmailStr | None = None

    consent_sms: bool = False

    consent_whatsapp: bool = False


# Used when updating patient information
class PatientUpdate(BaseModel):

    patient_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    date_of_birth: date | None = None

    gender: str | None = Field(
        default=None,
        max_length=20
    )

    phone_number: str | None = Field(
        default=None,
        min_length=10,
        max_length=20
    )

    email: EmailStr | None = None

    consent_sms: bool | None = None

    consent_whatsapp: bool | None = None

    is_active: bool | None = None


# Used when returning patient information
class PatientResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    patient_id: str
    patient_name: str
    date_of_birth: date | None
    gender: str | None
    phone_number: str
    email: str | None
    consent_sms: bool
    consent_whatsapp: bool
    is_active: bool
    created_at: datetime
