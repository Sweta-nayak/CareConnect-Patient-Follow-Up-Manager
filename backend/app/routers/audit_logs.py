
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles

from app.models.audit_log import AuditLog
from app.models.user import User

from app.schemas.audit_log import AuditLogResponse


router = APIRouter(
    prefix="/api/audit-logs",
    tags=["Audit Logs"]
)


# -----------------------------------------
# GET ALL AUDIT LOGS
# -----------------------------------------

@router.get(
    "/",
    response_model=list[AuditLogResponse]
)
def get_audit_logs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN"))
):

    audit_logs = db.scalars(

        select(AuditLog)
        .where(
            AuditLog.organization_id == current_user.organization_id
        )
        .order_by(
            AuditLog.created_at.desc()
        )
        .offset(offset)
        .limit(limit)

    ).all()

    return audit_logs


# -----------------------------------------
# GET AUDIT LOG BY ID
# -----------------------------------------

@router.get(
    "/{audit_id}",
    response_model=AuditLogResponse
)
def get_audit_log(
    audit_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN"))
):

    audit_log = db.scalar(

        select(AuditLog).where(
            AuditLog.audit_id == audit_id,
            AuditLog.organization_id == current_user.organization_id
        )

    )

    if not audit_log:

        raise HTTPException(
            status_code=404,
            detail="Audit log not found"
        )

    return audit_log
