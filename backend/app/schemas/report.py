from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ReportBase(BaseModel):
    title: str
    report_type: str  # executive_summary, sales_trends, support_analytics, full_ops
    format: str = "markdown"  # markdown, html, json, csv
    summary: str
    content: str
    metrics: Optional[Dict[str, Any]] = None


class ReportCreate(ReportBase):
    workflow_id: Optional[str] = None
    generated_by_agent: Optional[str] = "reporting"


class ReportResponse(ReportBase):
    id: str
    generated_by_agent: str
    workflow_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
