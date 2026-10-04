from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, record_audit_log
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    agent_filter: Optional[str] = Query(None, alias="agent"),
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve tasks with multi-dimensional filtering."""
    query = db.query(Task)

    if status_filter:
        query = query.filter(Task.status == status_filter)
    if priority_filter:
        query = query.filter(Task.priority == priority_filter)
    if agent_filter:
        query = query.filter(Task.assigned_agent == agent_filter)
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%") | Task.description.ilike(f"%{search}%"))

    return query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()


@router.post("", response_model=TaskResponse)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new manual task."""
    task = Task(
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        status=TaskStatus.PENDING.value,
        assigned_agent=task_in.assigned_agent,
        due_date=task_in.due_date,
        workflow_id=task_in.workflow_id,
        created_by_id=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    record_audit_log(db, action="TASK_CREATED", user_id=current_user.id, details={"task_id": task.id, "title": task.title})
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update task details or execution status."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if task_in.title is not None:
        task.title = task_in.title
    if task_in.description is not None:
        task.description = task_in.description
    if task_in.priority is not None:
        task.priority = task_in.priority
    if task_in.status is not None:
        task.status = task_in.status
        if task_in.status == TaskStatus.COMPLETED.value:
            task.completed_at = datetime.now(timezone.utc)
    if task_in.assigned_agent is not None:
        task.assigned_agent = task_in.assigned_agent
    if task_in.due_date is not None:
        task.due_date = task_in.due_date

    db.commit()
    db.refresh(task)
    return task
