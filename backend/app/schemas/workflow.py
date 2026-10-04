from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.schemas.approval import ApprovalResponse


class WorkflowStepCreate(BaseModel):
    step_order: int
    name: str
    description: Optional[str] = None
    agent_type: str
    input_data: Optional[Dict[str, Any]] = None
    requires_approval: bool = False


class WorkflowStepResponse(BaseModel):
    id: str
    workflow_id: str
    step_order: int
    name: str
    description: Optional[str] = None
    agent_type: str
    status: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    execution_time_ms: float
    error_message: Optional[str] = None
    requires_approval: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
    approval: Optional[ApprovalResponse] = None

    class Config:
        from_attributes = True


class WorkflowCreate(BaseModel):
    title: Optional[str] = None
    prompt: str
    auto_execute: bool = True


class WorkflowResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    prompt: str
    status: str
    current_step_index: int
    created_by_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    execution_metadata: Dict[str, Any]
    summary_result: Optional[str] = None
    steps: List[WorkflowStepResponse] = []
    approvals: List[ApprovalResponse] = []

    class Config:
        from_attributes = True


class WorkflowExecuteRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None
