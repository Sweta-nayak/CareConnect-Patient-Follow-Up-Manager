
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import User
from app.schemas.users import UserCreate, UserResponse
from app.security import hash_password


router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


# =========================================
# 1. CREATE USER
# Only ADMIN can create users
# =========================================

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles("ADMIN"))
):

    email = data.email.lower()

    existing_user = db.scalar(
        select(User).where(
            User.organization_id == current_admin.organization_id,
            User.email == email
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already registered in your organization"
        )

    new_user = User(
        organization_id=current_admin.organization_id,
        full_name=data.full_name,
        email=email,
        password_hash=hash_password(data.password),
        role=data.role
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create user. Check for duplicate information."
        )

    return new_user


# =========================================
# 2. GET ALL ACTIVE DOCTORS
# Admin, Doctor and Receptionist can view
# doctors in their own organization
# =========================================

@router.get(
    "/doctors",
    response_model=list[UserResponse]
)
def get_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DOCTOR", "RECEPTIONIST")
    )
):

    doctors = db.scalars(
        select(User).where(
            User.organization_id == current_user.organization_id,
            User.role == "DOCTOR",
            User.is_active == True
        ).order_by(User.full_name)
    ).all()

    return doctors
