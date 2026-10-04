import os
import uuid
import logging
from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.user import User, Organization, UserRole
from app.models.workflow import Workflow, WorkflowStep, WorkflowStatus, StepStatus
from app.models.approval import Approval, ApprovalStatus, RiskLevel
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.business import SalesRecord, SupportTicket, Report, AgentMetric
from app.models.document import Document, DocumentChunk
from app.models.audit import ActivityLog
from app.models.notification import Notification
from app.services.document_service import document_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database():
    db = SessionLocal()
    try:
        # 1. Organization
        org = db.query(Organization).first()
        if not org:
            org = Organization(
                name="Acme Enterprise Global",
                slug="acme-global"
            )
            db.add(org)
            db.flush()

        # 2. Users (Admin, Manager, Employee)
        users_to_seed = [
            ("admin@operations.ai", "Sarah Jenkins (Admin)", "admin123", UserRole.ADMIN.value),
            ("manager@operations.ai", "David Miller (Manager)", "manager123", UserRole.MANAGER.value),
            ("employee@operations.ai", "Alex Chen (Operations Analyst)", "employee123", UserRole.EMPLOYEE.value),
            ("admin@company.com", "Sarah Jenkins (Admin)", "AdminPass123!", UserRole.ADMIN.value),
            ("manager@company.com", "David Miller (Manager)", "ManagerPass123!", UserRole.MANAGER.value),
            ("employee@company.com", "Alex Chen (Operations Analyst)", "EmployeePass123!", UserRole.EMPLOYEE.value),
        ]
        created_users = {}
        for email, name, pwd, role in users_to_seed:
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(
                    email=email,
                    full_name=name,
                    hashed_password=get_password_hash(pwd),
                    role=role,
                    organization_id=org.id,
                    is_active=True
                )
                db.add(u)
                db.flush()
            created_users[email] = u

        admin = created_users.get("admin@operations.ai") or created_users.get("admin@company.com")
        manager = created_users.get("manager@operations.ai") or created_users.get("manager@company.com")
        employee = created_users.get("employee@operations.ai") or created_users.get("employee@company.com")

        # 3. Sales Records (Over $500,000+ realistic transaction volume)
        if db.query(SalesRecord).count() == 0:
            products = [
                ("Enterprise Cloud Hub", "Cloud Services", 125000.0, 18, "Apex Fintech Corp", "North America"),
                ("Autonomous Security Suite", "Cybersecurity", 84000.0, 24, "CyberShield Ltd", "EMEA"),
                ("Data Lakehouse Analytics", "Data Infrastructure", 152000.0, 12, "Vertex Global", "North America"),
                ("Real-Time AI Copilot", "AI Software", 49000.0, 42, "Starlight Retail", "APAC"),
                ("Customer 360 CRM", "SaaS Platform", 72000.0, 19, "Nexus Supply Chain", "EMEA"),
                ("Enterprise Cloud Hub", "Cloud Services", 28000.0, 2, "Helios Energy", "North America"),
                ("Autonomous Security Suite", "Cybersecurity", 62000.0, 10, "Titanium Bank", "APAC"),
                ("Data Lakehouse Analytics", "Data Infrastructure", 14200.0, -1, "Pacific Logistics", "APAC"),  # Refund anomaly
            ]
            
            for name, cat, amount, units, cust, reg in products:
                rec = SalesRecord(
                    product_name=name,
                    category=cat,
                    amount=amount,
                    units=units,
                    customer_name=cust,
                    region=reg,
                    status="refunded" if units < 0 else "completed",
                    transaction_date=datetime.now(timezone.utc) - timedelta(days=len(name) % 15)
                )
                db.add(rec)

        # 4. Support Tickets
        if db.query(SupportTicket).count() == 0:
            tickets = [
                (
                    "TK-8402", "Alex Mercer", "cto@acmecorp.com",
                    "Critical API Integration Outage on Checkout Pipeline",
                    "Production endpoints are returning 504 gateway timeouts when processing credit disbursements.",
                    "urgent", "technical", "open", "negative"
                ),
                (
                    "TK-8391", "Elena Rostova", "elena@vertex.io",
                    "Invoice Mismatch in Q3 Enterprise Billing Statement",
                    "Charged twice for data ingress fees amounting to $4,200 on billing account ACCT-991.",
                    "high", "billing", "in_progress", "negative"
                ),
                (
                    "TK-8380", "Marcus Vance", "marcus@starlight.com",
                    "Request for Single Sign-On (SSO) SAML Integration Assistance",
                    "Need Okta integration configuration guide and metadata XML certificate renewal.",
                    "medium", "account", "open", "neutral"
                ),
                (
                    "TK-8365", "Chloe Bennett", "cbennett@nexus.com",
                    "Automated PDF Ingestion Timeout on Large Scans",
                    "Documents over 50 pages trigger worker timeout in Document Analysis pipeline.",
                    "medium", "technical", "resolved", "neutral"
                ),
            ]

            for tnum, cname, cemail, subj, desc, prio, cat, stat, sent in tickets:
                t = SupportTicket(
                    ticket_number=tnum,
                    customer_name=cname,
                    customer_email=cemail,
                    subject=subj,
                    description=desc,
                    priority=prio,
                    category=cat,
                    status=stat,
                    ai_sentiment=sent,
                    created_at=datetime.now(timezone.utc) - timedelta(hours=int(tnum[-2:]))
                )
                db.add(t)

        # 5. Agent Metrics
        agents_data = [
            ("planner", "Task Planning Agent", "idle", 34, 34, 0, 240.5, 100.0),
            ("finance", "Finance Agent", "idle", 28, 27, 1, 385.0, 96.4),
            ("support", "Customer Support Agent", "idle", 41, 40, 1, 410.2, 97.5),
            ("reporting", "Executive Reporting Agent", "idle", 22, 22, 0, 520.0, 100.0),
            ("document", "Document Analysis Agent", "idle", 19, 19, 0, 315.8, 100.0),
        ]
        for atype, aname, astat, tot, succ, fail, lat, srate in agents_data:
            am = AgentMetric(
                agent_type=atype,
                name=aname,
                status=astat,
                total_tasks=tot,
                successful_tasks=succ,
                failed_tasks=fail,
                avg_execution_time_ms=lat,
                success_rate=srate,
                last_active_at=datetime.now(timezone.utc)
            )
            db.add(am)

        # 6. Sample Ingested Document
        sample_doc_text = """
ACME ENTERPRISE OPERATIONS & ESCALATION PROTOCOL 2026

1. Financial Discrepancies and Refunds:
Any refund exceeding $5,000 requires explicit authorization from a Finance Manager or Admin.
Automated systems may flag transactions but must never disburse funds without recorded human approval.

2. Critical Incident Response (SLA Level 1):
High-severity tickets such as payment gateway outages or enterprise customer checkout failures
must be acknowledged within 15 minutes and escalated directly to the On-Call Engineering Lead.

3. Document Ingestion Security:
All uploaded contracts and financial reports must be scanned, chunked, and embedded with strict
role-based access control. Unverified third-party scripts must not execute in the sandbox.
"""
        doc_id = str(uuid.uuid4())
        doc_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_Operations_Policy.txt")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(sample_doc_text)

        doc = Document(
            id=doc_id,
            filename="Operations_Policy.txt",
            file_type="txt",
            file_size=len(sample_doc_text.encode("utf-8")),
            file_path=doc_path,
            content_summary="Acme Enterprise standard operating procedures covering refunds, SLAs, and security.",
            raw_text=sample_doc_text,
            uploaded_by_id=admin.id
        )
        db.add(doc)

        chunks = document_service.chunk_text(sample_doc_text, chunk_size=200, overlap=30)
        for idx, chunk_text in enumerate(chunks):
            embedding_vec = document_service.compute_embedding(chunk_text)
            chunk_obj = DocumentChunk(
                document_id=doc.id,
                chunk_index=idx,
                content=chunk_text,
                embedding=embedding_vec,
                metadata_info={"filename": "Operations_Policy.txt", "section": idx + 1}
            )
            db.add(chunk_obj)

        # 7. Sample Completed Workflow
        wf1 = Workflow(
            title="Q3 Sales & Customer Support Comprehensive Audit",
            description="Deconstructed request into financial trend calculation, ticket backlog categorization, and summary reporting.",
            prompt="Analyze this month's sales data, identify top products, summarize pending customer complaints, and prepare an executive report.",
            status=WorkflowStatus.COMPLETED.value,
            current_step_index=4,
            created_by_id=manager.id,
            summary_result="Executive audit generated. Total revenue reached $482,500 (+14.2% YoY). Ticket #TK-8402 flagged for engineering escalation."
        )
        db.add(wf1)
        db.flush()

        step1 = WorkflowStep(
            workflow_id=wf1.id,
            step_order=1,
            name="Deconstruct Multi-Agent Plan",
            agent_type="planner",
            status=StepStatus.COMPLETED.value,
            execution_time_ms=210.4,
            completed_at=datetime.now(timezone.utc) - timedelta(minutes=25)
        )
        step2 = WorkflowStep(
            workflow_id=wf1.id,
            step_order=2,
            name="Execute Financial Anomaly Audit",
            agent_type="finance",
            status=StepStatus.COMPLETED.value,
            execution_time_ms=395.2,
            completed_at=datetime.now(timezone.utc) - timedelta(minutes=20)
        )
        step3 = WorkflowStep(
            workflow_id=wf1.id,
            step_order=3,
            name="Analyze Customer Complaint Severity",
            agent_type="support",
            status=StepStatus.COMPLETED.value,
            execution_time_ms=412.0,
            completed_at=datetime.now(timezone.utc) - timedelta(minutes=15)
        )
        step4 = WorkflowStep(
            workflow_id=wf1.id,
            step_order=4,
            name="Synthesize Executive Briefing Report",
            agent_type="reporting",
            status=StepStatus.COMPLETED.value,
            execution_time_ms=530.8,
            completed_at=datetime.now(timezone.utc) - timedelta(minutes=10)
        )
        db.add_all([step1, step2, step3, step4])

        # 8. Sample Pending Human-in-the-Loop Approval
        wf_pending = Workflow(
            title="High-Priority Customer Escalation & APAC Refund Notice",
            description="Escalation notification and financial reimbursement requiring manager sign-off.",
            prompt="Escalate ticket TK-8402 to tier-3 engineering and notify customer CTO with priority resolution commitment.",
            status=WorkflowStatus.WAITING_FOR_HUMAN.value,
            current_step_index=2,
            created_by_id=employee.id
        )
        db.add(wf_pending)
        db.flush()

        p_step = WorkflowStep(
            workflow_id=wf_pending.id,
            step_order=1,
            name="Draft Customer Escalation & Executive Email",
            agent_type="support",
            status=StepStatus.WAITING_APPROVAL.value,
            requires_approval=True
        )
        db.add(p_step)
        db.flush()

        approval = Approval(
            workflow_id=wf_pending.id,
            step_id=p_step.id,
            action_type="customer_escalation_and_email",
            title="Approve Customer Escalation Email (Ticket #TK-8402)",
            description="Customer Support Agent flagged an enterprise client SLA breach risk on API integration outage.",
            reason="High-value client (Acme Fintech Corp) has production checkout down. Requires manager approval before dispatching official SLA commitment email.",
            ai_explanation="The customer reported a 504 gateway timeout affecting client disbursements. The AI generated a formal acknowledgement promising tier-3 escalation within 1 hour.",
            data_payload={
                "ticket_number": "TK-8402",
                "recipient": "cto@acmecorp.com",
                "subject": "[URGENT] Engineering Escalation: API Integration Outage (Ticket #TK-8402)",
                "email_body": "Dear Alex, our tier-3 engineering team has been deployed to resolve the 504 gateway timeout on your production checkout endpoints. Updates will follow within 60 minutes."
            },
            agent_name="Customer Support Agent",
            risk_level=RiskLevel.CRITICAL.value,
            status=ApprovalStatus.PENDING.value
        )
        db.add(approval)

        # 9. In-App Notifications
        n1 = Notification(
            title="Approval Required: Critical Escalation",
            message="Customer Support Agent requires manager authorization to send priority escalation email for Ticket #TK-8402.",
            type="approval_required",
            user_id=manager.id,
            link_url="/approvals"
        )
        n2 = Notification(
            title="Executive Report Generated",
            message="Q3 Sales & Customer Support Comprehensive Audit report is ready for download.",
            type="workflow_completed",
            user_id=None,
            link_url="/reports"
        )
        db.add_all([n1, n2])

        # 10. Activity Logs
        logs = [
            ActivityLog(user_id=admin.id, action="USER_LOGIN", details={"ip": "192.168.1.10"}),
            ActivityLog(user_id=manager.id, action="WORKFLOW_CREATED", workflow_id=wf1.id, details={"title": wf1.title}),
            ActivityLog(action="AI_AGENT_PLANNER_COMPLETED", agent="planner", workflow_id=wf1.id, details={"status": "SUCCESS"}),
            ActivityLog(action="APPROVAL_REQUESTED", agent="support", workflow_id=wf_pending.id, details={"approval_id": approval.id}),
        ]
        db.add_all(logs)

        db.commit()
        logger.info("Demo data seeded successfully!")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
