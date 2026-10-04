from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role, record_audit_log
from app.models.user import User, UserRole
from app.models.approval import Approval, ApprovalStatus
from app.models.workflow import WorkflowStep, StepStatus
from app.schemas.approval import ApprovalResponse, ApprovalActionRequest, ApprovalModifyRequest
from app.agents.orchestrator import Orchestrator

router = APIRouter(prefix="/approvals", tags=["Human-in-the-Loop Approvals"])


@router.get("", response_model=List[ApprovalResponse])
def list_approvals(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List pending and historical approval requests."""
    query = db.query(Approval)
    if status_filter:
        query = query.filter(Approval.status == status_filter)
    return query.order_by(Approval.requested_at.desc()).all()


@router.post("/{approval_id}/action", response_model=ApprovalResponse)
async def process_approval_action(
    approval_id: str,
    request: ApprovalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN.value, UserRole.MANAGER.value]))
):
    """
    Approve or Reject a pending sensitive AI action.
    Strictly restricted to Managers and Admins.
    """
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")

    if approval.status != ApprovalStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approval has already been processed.")

    action_clean = request.action.lower()
    is_approved = (action_clean == "approve")

    approval.status = ApprovalStatus.APPROVED.value if is_approved else ApprovalStatus.REJECTED.value
    approval.reviewed_at = datetime.now(timezone.utc)
    approval.reviewed_by_id = current_user.id
    approval.review_notes = request.review_notes
    db.commit()

    record_audit_log(
        db,
        action="APPROVAL_GRANTED" if is_approved else "APPROVAL_REJECTED",
        user_id=current_user.id,
        workflow_id=approval.workflow_id,
        details={"approval_id": approval.id, "action_type": approval.action_type, "notes": request.review_notes}
    )

    # Resume workflow execution through Orchestrator
    await Orchestrator.resume_workflow(approval.workflow_id, db, reviewer_id=current_user.id, approved=is_approved)

    db.refresh(approval)
    return approval


@router.post("/{approval_id}/modify", response_model=ApprovalResponse)
async def modify_and_approve(
    approval_id: str,
    request: ApprovalModifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN.value, UserRole.MANAGER.value]))
):
    """Modify parameters of sensitive action and authorize execution."""
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")

    approval.status = ApprovalStatus.MODIFIED.value
    approval.reviewed_at = datetime.now(timezone.utc)
    approval.reviewed_by_id = current_user.id
    approval.review_notes = request.review_notes
    approval.modification_payload = request.modification_payload
    approval.data_payload = request.modification_payload
    db.commit()

    record_audit_log(
        db,
        action="APPROVAL_MODIFIED_AND_GRANTED",
        user_id=current_user.id,
        workflow_id=approval.workflow_id,
        details={"approval_id": approval.id, "modified_payload": request.modification_payload}
    )

    await Orchestrator.resume_workflow(approval.workflow_id, db, reviewer_id=current_user.id, approved=True)

    db.refresh(approval)
    return approval
