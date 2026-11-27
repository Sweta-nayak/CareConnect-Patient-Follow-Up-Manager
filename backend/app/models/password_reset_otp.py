from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    CHAR,
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Index
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PasswordResetOTP(Base):
    __tablename__ = "password_reset_otps"

    otp_id: Mapped[str] = mapped_column(
    CHAR(36),
    primary_key=True,
    default=lambda: str(uuid.uuid4())
)

    organization_id: Mapped[str] = mapped_column(
    CHAR(36),
    ForeignKey("organizations.organization_id"),
    nullable=False
)

    user_id: Mapped[str] = mapped_column(
    CHAR(36),
    ForeignKey("users.user_id"),
    nullable=False
)

    otp_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


Index(
    "idx_password_reset_user",
    PasswordResetOTP.organization_id,
    PasswordResetOTP.user_id
)