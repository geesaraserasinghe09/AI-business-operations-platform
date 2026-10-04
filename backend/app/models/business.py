import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class SalesRecord(Base):
    __tablename__ = "sales_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    units = Column(Integer, nullable=False)
    customer_name = Column(String(255), nullable=False)
    region = Column(String(100), nullable=False, index=True)
    transaction_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    status = Column(String(50), default="completed")  # completed, refunded, pending


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium", index=True)  # low, medium, high, urgent
    category = Column(String(100), nullable=False, index=True)   # billing, technical, account, complaint
    status = Column(String(50), default="open", index=True)      # open, in_progress, resolved, escalated
    resolution_notes = Column(Text, nullable=True)
    ai_sentiment = Column(String(50), nullable=True)             # negative, neutral, positive
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False, index=True)  # executive_summary, sales_trends, support_analytics, full_ops
    format = Column(String(20), default="markdown")                # markdown, html, json, csv
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    metrics = Column(JSON, default=dict)
    generated_by_agent = Column(String(50), default="reporting")
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    workflow = relationship("Workflow", back_populates="reports")


class AgentMetric(Base):
    __tablename__ = "agent_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_type = Column(String(50), unique=True, nullable=False)  # planner, finance, support, reporting, document
    name = Column(String(100), nullable=False)
    status = Column(String(50), default="idle")                   # idle, executing, paused, error
    current_task = Column(String(255), nullable=True)
    total_tasks = Column(Integer, default=0)
    successful_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    avg_execution_time_ms = Column(Float, default=0.0)
    success_rate = Column(Float, default=100.0)
    last_active_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
