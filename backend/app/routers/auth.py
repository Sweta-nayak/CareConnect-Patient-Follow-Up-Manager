
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import OrganizationRegister, LoginRequest
from fastapi import HTTPException, status

from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ResetPasswordRequest
)

from app.services.password_reset_service import (
    request_password_reset,
    reset_password_with_otp
)
from app.services.auth_service import (
    register_organization,
    login_user
)
from app.dependencies import get_current_user
from app.models import User


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# ==========================================
# ORGANIZATION REGISTRATION API
# ==========================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(
    data: OrganizationRegister,
    db: Session = Depends(get_db)
):
    try:
        result = register_organization(db, data)
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )


# ==========================================
# USER LOGIN API
# ==========================================

@router.post(
    "/login",
    status_code=status.HTTP_200_OK
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        result = login_user(db, data)
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error)
        )


# ==========================================
# GET CURRENT LOGGED-IN USER API
# ==========================================

@router.get(
    "/me",
    status_code=status.HTTP_200_OK
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "Authentication successful",
        "user_id": current_user.user_id,
        "organization_id": current_user.organization_id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role
    }
@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    message = request_password_reset(
        db=db,
        organization_code=data.organization_code,
        email=str(data.email)
    )

    return {
        "message": message
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    try:
        message = reset_password_with_otp(
            db=db,
            organization_code=data.organization_code,
            email=str(data.email),
            entered_otp=data.otp,
            new_password=data.new_password
        )

        return {
            "message": message
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
