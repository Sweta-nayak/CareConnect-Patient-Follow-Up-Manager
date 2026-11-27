
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Literal["DOCTOR", "RECEPTIONIST"]


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
