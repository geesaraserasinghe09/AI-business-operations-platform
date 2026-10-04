from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.workflow import Workflow, WorkflowStatus
from app.models.approval import Approval, ApprovalStatus
from app.models.business import SalesRecord, SupportTicket, AgentMetric
from app.schemas.business import DashboardStatsResponse, AgentMetricResponse

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard"])


@router.get("/dashboard", response_model=DashboardStatsResponse)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve unified executive dashboard statistics, charts, and operational telemetry."""
    total_tasks = db.query(Task).count()
    active_workflows = db.query(Workflow).filter(Workflow.status.in_([WorkflowStatus.RUNNING.value, WorkflowStatus.WAITING_FOR_HUMAN.value])).count()
    completed_workflows = db.query(Workflow).filter(Workflow.status == WorkflowStatus.COMPLETED.value).count()
    failed_workflows = db.query(Workflow).filter(Workflow.status == WorkflowStatus.FAILED.value).count()
    pending_approvals = db.query(Approval).filter(Approval.status == ApprovalStatus.PENDING.value).count()

    total_revenue = db.query(func.sum(SalesRecord.amount)).scalar() or 0.0
    total_tickets = db.query(SupportTicket).count()
    open_tickets = db.query(SupportTicket).filter(SupportTicket.status.in_(["open", "in_progress"])).count()

    # Agent activity
    agents = db.query(AgentMetric).all()
    if not agents:
        # Pre-seed metrics if empty
        defaults = [
            ("planner", "Task Planning Agent"),
            ("finance", "Finance Agent"),
            ("support", "Customer Support Agent"),
            ("reporting", "Executive Reporting Agent"),
            ("document", "Document Analysis Agent"),
        ]
        for a_type, a_name in defaults:
            metric = AgentMetric(
                agent_type=a_type,
                name=a_name,
                status="idle",
                total_tasks=14,
                successful_tasks=14,
                failed_tasks=0,
                avg_execution_time_ms=310.5,
                success_rate=100.0
            )
            db.add(metric)
        db.commit()
        agents = db.query(AgentMetric).all()

    # Recent workflows
    recent_wf = (
        db.query(Workflow)
        .order_by(Workflow.created_at.desc())
        .limit(5)
        .all()
    )
    recent_wf_list = [
        {
            "id": w.id,
            "title": w.title,
            "status": w.status,
            "created_at": w.created_at.isoformat(),
            "steps_count": len(w.steps)
        }
        for w in recent_wf
    ]

    # Monthly sales chart
    monthly_sales = [
        {"month": "May", "sales": 64200, "target": 60000},
        {"month": "Jun", "sales": 78900, "target": 70000},
        {"month": "Jul", "sales": 89400, "target": 80000},
        {"month": "Aug", "sales": 96100, "target": 90000},
        {"month": "Sep", "sales": 112500, "target": 100000},
        {"month": "Oct", "sales": 138400, "target": 120000},
    ]

    # Ticket distribution
    ticket_cats = (
        db.query(SupportTicket.category, func.count(SupportTicket.id))
        .group_by(SupportTicket.category)
        .all()
    )
    ticket_distribution = [{"name": c[0].capitalize(), "value": c[1]} for c in ticket_cats]
    if not ticket_distribution:
        ticket_distribution = [
            {"name": "Billing", "value": 12},
            {"name": "Technical", "value": 19},
            {"name": "API Integration", "value": 8},
            {"name": "Account", "value": 6}
        ]

    return DashboardStatsResponse(
        total_tasks=total_tasks,
        active_workflows=active_workflows,
        completed_workflows=completed_workflows,
        pending_approvals=pending_approvals,
        failed_workflows=failed_workflows,
        total_revenue=round(float(total_revenue), 2),
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        system_health="Operational",
        agent_activity=agents,
        recent_workflows=recent_wf_list,
        monthly_sales_chart=monthly_sales,
        ticket_distribution=ticket_distribution
    )
