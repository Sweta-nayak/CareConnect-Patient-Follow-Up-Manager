
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    organization_id: str,
    actor_user_id: str | None,
    action: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    details: dict | None = None
):
    """
    Add an audit record to the current database transaction.

    The calling API should commit the transaction after
    its main operation and audit record have been added.
    """

    audit_record = AuditLog(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )

    db.add(audit_record)

    return audit_record
