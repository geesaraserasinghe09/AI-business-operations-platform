import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., USER_LOGIN, WORKFLOW_CREATED, AI_AGENT_STARTED, APPROVAL_GRANTED
    agent = Column(String(50), nullable=True, index=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=True, index=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(50), nullable=True)
    result_status = Column(String(50), default="SUCCESS")     # SUCCESS, FAILED, PENDING
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="activity_logs")
