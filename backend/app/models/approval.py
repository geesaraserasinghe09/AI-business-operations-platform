import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False, index=True)
    step_id = Column(String(36), ForeignKey("workflow_steps.id"), nullable=True, index=True)
    
    action_type = Column(String(100), nullable=False)  # e.g., "send_email", "database_update", "refund_process", "escalate_ticket"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    ai_explanation = Column(Text, nullable=False)
    data_payload = Column(JSON, default=dict)
    
    agent_name = Column(String(50), nullable=False)
    risk_level = Column(String(20), default=RiskLevel.MEDIUM.value, nullable=False)
    status = Column(String(20), default=ApprovalStatus.PENDING.value, index=True, nullable=False)
    
    requested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    review_notes = Column(Text, nullable=True)
    modification_payload = Column(JSON, nullable=True)

    # Relationships
    workflow = relationship("Workflow", back_populates="approvals")
    step = relationship("WorkflowStep", back_populates="approval")
    reviewed_by_user = relationship("User", back_populates="approvals_reviewed")
