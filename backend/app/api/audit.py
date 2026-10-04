from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.models.audit import ActivityLog
from app.schemas.audit import ActivityLogResponse

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@router.get("", response_model=List[ActivityLogResponse])
def list_audit_logs(
    action: Optional[str] = None,
    agent: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN.value, UserRole.MANAGER.value]))
):
    """Retrieve immutable audit trail records with filters (Admins & Managers only)."""
    query = db.query(ActivityLog)
    if action:
        query = query.filter(ActivityLog.action == action)
    if agent:
        query = query.filter(ActivityLog.agent == agent)

    logs = query.order_by(ActivityLog.timestamp.desc()).offset(offset).limit(limit).all()
    results = []
    for l in logs:
        results.append(ActivityLogResponse(
            id=l.id,
            user_id=l.user_id,
            user_name=l.user.full_name if l.user else "System / Agent",
            action=l.action,
            agent=l.agent,
            workflow_id=l.workflow_id,
            details=l.details or {},
            ip_address=l.ip_address,
            result_status=l.result_status,
            timestamp=l.timestamp
        ))
    return results
