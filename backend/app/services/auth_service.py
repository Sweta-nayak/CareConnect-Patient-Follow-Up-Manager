
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Organization, User
from app.schemas.auth import OrganizationRegister, LoginRequest
from app.security import (
    hash_password,
    verify_password,
    create_access_token
)


# ==========================================
# ORGANIZATION REGISTRATION
# ==========================================

def register_organization(
    db: Session,
    data: OrganizationRegister
) -> dict:

    # Normalize user input
    organization_code = data.organization_code.strip().upper()
    email = str(data.email).strip().lower()

    # Check whether organization code already exists
    existing_org = db.scalar(
        select(Organization).where(
            Organization.organization_code == organization_code
        )
    )

    if existing_org:
        raise ValueError("Organization code already exists")

    try:
        # Create organization
        organization = Organization(
            organization_name=data.organization_name.strip(),
            organization_code=organization_code
        )

        db.add(organization)

        # Save organization temporarily to generate its ID
        db.flush()

        # Create first administrator
        admin = User(
            organization_id=organization.organization_id,
            full_name=data.full_name.strip(),
            email=email,
            password_hash=hash_password(data.password),
            role="ADMIN"
        )

        db.add(admin)

        # Save both records together
        db.commit()

        return {
            "message": "Organization registered successfully",
            "organization_id": organization.organization_id,
            "organization_name": organization.organization_name,
            "admin_user_id": admin.user_id,
            "admin_email": admin.email,
            "role": admin.role
        }

    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "Registration failed. Organization code or admin email may already exist."
        ) from error

    except Exception:
        db.rollback()
        raise


# ==========================================
# USER LOGIN
# ==========================================

def login_user(
    db: Session,
    data: LoginRequest
) -> dict:

    # Normalize user input
    organization_code = data.organization_code.strip().upper()
    email = str(data.email).strip().lower()

    # Find organization using organization code
    organization = db.scalar(
        select(Organization).where(
            Organization.organization_code == organization_code
        )
    )

    if not organization:
        raise ValueError("Invalid organization code or credentials")

    # Check whether organization is active
    if not organization.is_active:
        raise ValueError("Organization account is inactive")

    # Find user within the selected organization
    user = db.scalar(
        select(User).where(
            User.organization_id == organization.organization_id,
            User.email == email
        )
    )

    if not user:
        raise ValueError("Invalid organization code or credentials")

    # Verify entered password against stored password hash
    if not verify_password(data.password, user.password_hash):
        raise ValueError("Invalid organization code or credentials")

    # Check whether user account is active
    if not user.is_active:
        raise ValueError("User account is inactive")

    # Get role as a string
    role = user.role

    # Generate JWT access token
    access_token = create_access_token(
        user.user_id,
        user.organization_id,
        role
    )

    # Return login response
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "organization_id": user.organization_id,
        "organization_name": organization.organization_name,
        "full_name": user.full_name,
        "email": user.email,
        "role": role
    }
