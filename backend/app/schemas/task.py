from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"  # low, medium, high, urgent
    assigned_agent: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    workflow_id: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_agent: Optional[str] = None
    due_date: Optional[datetime] = None
    approval_status: Optional[str] = None


class TaskResponse(TaskBase):
    id: str
    status: str
    created_by_id: Optional[str] = None
    workflow_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    result_data: Dict[str, Any]
    approval_status: Optional[str] = None

    class Config:
        from_attributes = True
