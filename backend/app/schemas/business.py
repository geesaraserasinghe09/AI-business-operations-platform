from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class SalesRecordResponse(BaseModel):
    id: str
    product_name: str
    category: str
    amount: float
    units: int
    customer_name: str
    region: str
    transaction_date: datetime
    status: str

    class Config:
        from_attributes = True


class SupportTicketResponse(BaseModel):
    id: str
    ticket_number: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    priority: str
    category: str
    status: str
    resolution_notes: Optional[str] = None
    ai_sentiment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentMetricResponse(BaseModel):
    id: str
    agent_type: str
    name: str
    status: str
    current_task: Optional[str] = None
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    avg_execution_time_ms: float
    success_rate: float
    last_active_at: datetime

    class Config:
        from_attributes = True


class DashboardStatsResponse(BaseModel):
    total_tasks: int
    active_workflows: int
    completed_workflows: int
    pending_approvals: int
    failed_workflows: int
    total_revenue: float
    total_tickets: int
    open_tickets: int
    system_health: str = "Optimal"
    agent_activity: List[AgentMetricResponse]
    recent_workflows: List[Dict[str, Any]]
    monthly_sales_chart: List[Dict[str, Any]]
    ticket_distribution: List[Dict[str, Any]]
