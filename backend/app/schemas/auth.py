
from pydantic import BaseModel, EmailStr, Field


class OrganizationRegister(BaseModel):
    organization_name: str = Field(
        min_length=2,
        max_length=100
    )

    organization_code: str = Field(
        min_length=3,
        max_length=50
    )

    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

class LoginRequest(BaseModel):

    organization_code: str = Field(
        min_length=3,
        max_length=50
    )

    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128
    )

