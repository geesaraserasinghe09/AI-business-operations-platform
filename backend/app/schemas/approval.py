from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ApprovalActionRequest(BaseModel):
    action: str  # "approve" or "reject"
    review_notes: Optional[str] = None


class ApprovalModifyRequest(BaseModel):
    modification_payload: Dict[str, Any]
    review_notes: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: str
    workflow_id: str
    step_id: Optional[str] = None
    action_type: str
    title: str
    description: str
    reason: str
    ai_explanation: str
    data_payload: Dict[str, Any]
    agent_name: str
    risk_level: str
    status: str
    requested_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by_id: Optional[str] = None
    review_notes: Optional[str] = None
    modification_payload: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
