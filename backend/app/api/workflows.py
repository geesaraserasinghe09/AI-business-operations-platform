from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, record_audit_log
from app.models.user import User
from app.models.workflow import Workflow, WorkflowStatus
from app.schemas.workflow import WorkflowCreate, WorkflowResponse
from app.agents.orchestrator import Orchestrator

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("", response_model=List[WorkflowResponse])
def list_workflows(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflows with filtering and search capabilities."""
    query = db.query(Workflow)

    if status_filter:
        query = query.filter(Workflow.status == status_filter)
    if search:
        query = query.filter(Workflow.title.ilike(f"%{search}%") | Workflow.prompt.ilike(f"%{search}%"))

    # Employees only see their own workflows; Managers and Admins see all
    if current_user.role == "employee":
        query = query.filter(Workflow.created_by_id == current_user.id)

    return query.order_by(Workflow.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get full details of a specific workflow, including all steps and approvals."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    if current_user.role == "employee" and workflow.created_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return workflow


@router.post("", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a natural-language business request to the AI Orchestration layer.
    Automatically breaks down tasks and starts execution graph.
    """
    workflow = Workflow(
        title=request.title or f"Workflow: {request.prompt[:40]}...",
        prompt=request.prompt,
        status=WorkflowStatus.RUNNING.value,
        created_by_id=current_user.id,
        execution_metadata={"initiated_by": current_user.email}
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    record_audit_log(
        db,
        action="WORKFLOW_CREATED",
        user_id=current_user.id,
        workflow_id=workflow.id,
        details={"prompt": request.prompt}
    )

    if request.auto_execute:
        # Run orchestrated multi-agent steps
        workflow = await Orchestrator.run_workflow(workflow.id, db, user_id=current_user.id)

    return workflow


@router.post("/{workflow_id}/retry", response_model=WorkflowResponse)
async def retry_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retry execution of a failed or halted workflow."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    workflow.status = WorkflowStatus.RUNNING.value
    db.commit()

    record_audit_log(
        db,
        action="WORKFLOW_RETRIED",
        user_id=current_user.id,
        workflow_id=workflow.id
    )

    return await Orchestrator.run_workflow(workflow.id, db, user_id=current_user.id)
