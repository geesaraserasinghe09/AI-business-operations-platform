from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.business import AgentMetric
from app.schemas.business import AgentMetricResponse

router = APIRouter(prefix="/agents", tags=["AI Agents Monitoring"])


@router.get("", response_model=List[AgentMetricResponse])
def list_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve runtime status, efficiency metrics, and health of all specialized agents."""
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
                total_tasks=12,
                successful_tasks=12,
                failed_tasks=0,
                avg_execution_time_ms=340.5,
                success_rate=100.0
            )
            db.add(metric)
        db.commit()
        agents = db.query(AgentMetric).all()

    return agents


@router.post("/{agent_type}/toggle-status")
def toggle_agent_status(
    agent_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN.value, UserRole.MANAGER.value]))
):
    """Toggle agent operational status between idle and paused."""
    agent = db.query(AgentMetric).filter(AgentMetric.agent_type == agent_type).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    agent.status = "paused" if agent.status != "paused" else "idle"
    db.commit()
    db.refresh(agent)
    return {"agent_type": agent.agent_type, "status": agent.status}
