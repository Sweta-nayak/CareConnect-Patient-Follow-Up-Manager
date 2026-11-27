
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):

    audit_id: str
    organization_id: str
    actor_user_id: str | None

    action: str
    entity_type: str | None
    entity_id: str | None

    details: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
