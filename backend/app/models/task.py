import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    priority = Column(String(20), default=TaskPriority.MEDIUM.value, nullable=False, index=True)
    status = Column(String(20), default=TaskStatus.PENDING.value, nullable=False, index=True)
    assigned_agent = Column(String(50), nullable=True, index=True)
    
    created_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=True, index=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    result_data = Column(JSON, default=dict)
    approval_status = Column(String(50), nullable=True)

    # Relationships
    created_by_user = relationship("User", back_populates="tasks")
    workflow = relationship("Workflow", back_populates="tasks")
