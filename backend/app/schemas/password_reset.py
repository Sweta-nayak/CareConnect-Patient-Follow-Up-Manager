from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    organization_code: str = Field(
        min_length=3,
        max_length=50
    )

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    organization_code: str = Field(
        min_length=3,
        max_length=50
    )

    email: EmailStr

    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$"
    )

    new_password: str = Field(
        min_length=8,
        max_length=128
    )