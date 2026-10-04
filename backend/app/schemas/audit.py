from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ActivityLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    agent: Optional[str] = None
    workflow_id: Optional[str] = None
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    result_status: str
    timestamp: datetime

    class Config:
        from_attributes = True
