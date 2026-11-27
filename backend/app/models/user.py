
import uuid

from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
    text
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):

    __tablename__ = "users"

    # Primary Key
    user_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Organization Foreign Key
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.organization_id"),
        nullable=False
    )

    # User Name
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Email
    email: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    # Hashed Password
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # User Role
    role: Mapped[str] = mapped_column(
        Enum(
            "ADMIN",
            "DOCTOR",
            "RECEPTIONIST",
            name="user_role"
        ),
        nullable=False
    )

    # Active Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("1")
    )

    # Created Date
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    # Unique Constraints
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "email",
            name="uq_user_org_email"
        ),

        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_user_org_id"
        ),
    )
