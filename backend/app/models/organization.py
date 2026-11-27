
import uuid

from sqlalchemy import String, Boolean, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Organization(Base):

    __tablename__ = "organizations"

    # Primary Key
    organization_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Organization Name
    organization_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Unique Organization Code
    organization_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    # Active Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("1")
    )

    # Creation Date
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )
