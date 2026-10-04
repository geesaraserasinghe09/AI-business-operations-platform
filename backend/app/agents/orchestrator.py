import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.agents.planner_agent import PlannerAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.support_agent import SupportAgent
from app.agents.document_agent import DocumentAgent
from app.agents.reporting_agent import ReportingAgent

from app.models.workflow import Workflow, WorkflowStep, WorkflowStatus, StepStatus
from app.models.approval import Approval, ApprovalStatus, RiskLevel
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.business import Report, AgentMetric
from app.models.audit import ActivityLog
from app.models.notification import Notification

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Central Multi-Agent Orchestration Engine.
    Coordinates specialized agents through a defined workflow graph,
    enforces Human-in-the-Loop checkpoints, and maintains immutable state.
    """

    @staticmethod
    def _update_agent_metric(db: Session, agent_type: str, success: bool, duration_ms: float):
        """Update telemetry metrics for monitored agents."""
        metric = db.query(AgentMetric).filter(AgentMetric.agent_type == agent_type).first()
        if not metric:
            name_map = {
                "planner": "Task Planning Agent",
                "finance": "Finance Agent",
                "support": "Customer Support Agent",
                "document": "Document Analysis Agent",
                "reporting": "Executive Reporting Agent"
            }
            metric = AgentMetric(
                agent_type=agent_type,
                name=name_map.get(agent_type, f"{agent_type.capitalize()} Agent"),
                total_tasks=0,
                successful_tasks=0,
                failed_tasks=0,
                avg_execution_time_ms=0.0,
                success_rate=100.0,
                status="idle"
            )
            db.add(metric)
            db.flush()

        metric.total_tasks += 1
        if success:
            metric.successful_tasks += 1
        else:
            metric.failed_tasks += 1

        # Running average for latency
        if metric.total_tasks > 0:
            metric.avg_execution_time_ms = round(
                (metric.avg_execution_time_ms * (metric.total_tasks - 1) + duration_ms) / metric.total_tasks, 1
            )
            metric.success_rate = round((metric.successful_tasks / metric.total_tasks) * 100.0, 1)

        metric.last_active_at = datetime.now(timezone.utc)
        metric.status = "idle"
        db.commit()

    @staticmethod
    async def run_workflow(workflow_id: str, db: Session, user_id: Optional[str] = None) -> Workflow:
        """
        Execute an orchestrated multi-agent workflow sequentially through its task graph.
        Haults and registers approvals if high-impact actions are encountered.
        """
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found.")

        workflow.status = WorkflowStatus.RUNNING.value
        db.commit()

        # Initialize State
        state: AgentState = {
            "workflow_id": workflow.id,
            "user_id": user_id,
            "prompt": workflow.prompt,
            "steps": [],
            "current_step_index": 0,
            "agent_outputs": {},
            "approval_required": False,
            "approval_payload": None,
            "is_paused_for_human": False,
            "summary_result": None,
            "errors": []
        }

        # -------------------------------------------------------------
        # STEP 1: Task Planning Agent (Only if steps not already planned)
        # -------------------------------------------------------------
        existing_steps = db.query(WorkflowStep).filter(WorkflowStep.workflow_id == workflow.id).order_by(WorkflowStep.step_order).all()
        if not existing_steps:
            t0 = time.time()
            try:
                state = await PlannerAgent.plan(state)
                plan = state.get("plan", {})
                tasks = plan.get("tasks", [])
                plan_duration = (time.time() - t0) * 1000

                workflow.title = plan.get("workflow_title", workflow.title)
                workflow.description = plan.get("summary", "")
                
                # Persist Planned Steps in database
                for idx, task_info in enumerate(tasks):
                    step = WorkflowStep(
                        workflow_id=workflow.id,
                        step_order=idx + 1,
                        name=task_info.get("name", f"Step {idx + 1}"),
                        description=task_info.get("description", ""),
                        agent_type=task_info.get("agent_type", "planner"),
                        status=StepStatus.PENDING.value,
                        requires_approval=task_info.get("requires_approval", False)
                    )
                    db.add(step)

                    # Also create corresponding entry in Task model
                    user_task = Task(
                        title=task_info.get("name", f"Step {idx + 1}"),
                        description=task_info.get("description", ""),
                        priority=TaskPriority.HIGH.value if task_info.get("requires_approval") else TaskPriority.MEDIUM.value,
                        status=TaskStatus.PENDING.value,
                        assigned_agent=task_info.get("agent_type"),
                        created_by_id=user_id,
                        workflow_id=workflow.id
                    )
                    db.add(user_task)

                db.commit()
                Orchestrator._update_agent_metric(db, "planner", True, plan_duration)

            except Exception as e:
                logger.error(f"Planning failed: {e}")
                workflow.status = WorkflowStatus.FAILED.value
                workflow.summary_result = f"Planning failed: {str(e)}"
                db.commit()
                return workflow

        # Reload persisted steps
        steps = db.query(WorkflowStep).filter(WorkflowStep.workflow_id == workflow.id).order_by(WorkflowStep.step_order).all()

        # -------------------------------------------------------------
        # STEP 2: Execute Workflow Steps through Specialized Agents
        # -------------------------------------------------------------
        for step in steps:
            # Skip steps that are already completed
            if step.status == StepStatus.COMPLETED.value:
                continue

            workflow.current_step_index = step.step_order
            step.status = StepStatus.RUNNING.value
            db.commit()

            start_t = time.time()
            agent_type = step.agent_type.lower()
            step_success = True
            error_msg = None

            try:
                # Route to specialized agent
                if agent_type == "finance":
                    state = await FinanceAgent.execute(state, db)
                    step.output_data = state.get("agent_outputs", {}).get("finance", {})
                elif agent_type == "support":
                    state = await SupportAgent.execute(state, db)
                    step.output_data = state.get("agent_outputs", {}).get("support", {})
                elif agent_type == "document":
                    state = await DocumentAgent.execute(state, db)
                    step.output_data = state.get("agent_outputs", {}).get("document", {})
                elif agent_type == "reporting":
                    state = await ReportingAgent.execute(state)
                    step.output_data = state.get("agent_outputs", {}).get("reporting", {})
                    
                    # Also persist final report entity
                    rep_payload = state.get("agent_outputs", {}).get("reporting", {})
                    new_report = Report(
                        title=rep_payload.get("title", f"Report: {workflow.title}"),
                        report_type="executive_summary",
                        format="markdown",
                        summary=rep_payload.get("summary", ""),
                        content=rep_payload.get("markdown_content", ""),
                        metrics=rep_payload.get("metadata", {}),
                        generated_by_agent="reporting",
                        workflow_id=workflow.id
                    )
                    db.add(new_report)

                duration_ms = (time.time() - start_t) * 1000
                step.execution_time_ms = round(duration_ms, 1)

                # Check if this agent triggered a Human-in-the-Loop Approval requirement
                if state.get("approval_required") and state.get("approval_payload"):
                    payload = state["approval_payload"]
                    step.status = StepStatus.WAITING_APPROVAL.value
                    
                    approval = Approval(
                        workflow_id=workflow.id,
                        step_id=step.id,
                        action_type=payload.get("action_type", "sensitive_action"),
                        title=payload.get("title", "Approval Required"),
                        description=payload.get("description", ""),
                        reason=payload.get("reason", "Sensitive operation triggered"),
                        ai_explanation=payload.get("ai_explanation", ""),
                        data_payload=payload.get("data_payload", {}),
                        agent_name=payload.get("agent_name", agent_type),
                        risk_level=payload.get("risk_level", RiskLevel.HIGH.value),
                        status=ApprovalStatus.PENDING.value
                    )
                    db.add(approval)

                    # Update associated task
                    t_record = db.query(Task).filter(Task.workflow_id == workflow.id, Task.title == step.name).first()
                    if t_record:
                        t_record.status = TaskStatus.BLOCKED.value
                        t_record.approval_status = "pending_approval"

                    # Generate Notification
                    notif = Notification(
                        title=f"Approval Required: {approval.title}",
                        message=f"{approval.agent_name} requires manager authorization for action: {approval.action_type}",
                        type="approval_required",
                        user_id=user_id,
                        link_url="/approvals"
                    )
                    db.add(notif)

                    # Pause workflow execution at this checkpoint
                    workflow.status = WorkflowStatus.WAITING_FOR_HUMAN.value
                    state["is_paused_for_human"] = True
                    state["approval_required"] = False  # Reset flag for this cycle

                    Orchestrator._update_agent_metric(db, agent_type, True, duration_ms)
                    db.commit()
                    return workflow

                step.status = StepStatus.COMPLETED.value
                step.completed_at = datetime.now(timezone.utc)

                # Update Task
                t_record = db.query(Task).filter(Task.workflow_id == workflow.id, Task.title == step.name).first()
                if t_record:
                    t_record.status = TaskStatus.COMPLETED.value
                    t_record.completed_at = datetime.now(timezone.utc)
                    t_record.result_data = step.output_data

                Orchestrator._update_agent_metric(db, agent_type, True, duration_ms)

            except Exception as ex:
                duration_ms = (time.time() - start_t) * 1000
                step.status = StepStatus.FAILED.value
                step.error_message = str(ex)
                step_success = False
                error_msg = str(ex)
                Orchestrator._update_agent_metric(db, agent_type, False, duration_ms)
                logger.error(f"Error in step '{step.name}': {ex}")

            db.commit()

            # Record audit trail for step completion
            log = ActivityLog(
                user_id=user_id,
                action=f"AI_AGENT_{step.agent_type.upper()}_COMPLETED",
                agent=step.agent_type,
                workflow_id=workflow.id,
                details={"step_name": step.name, "status": step.status, "duration_ms": step.execution_time_ms},
                result_status="SUCCESS" if step_success else "FAILED"
            )
            db.add(log)
            db.commit()

            if not step_success:
                workflow.status = WorkflowStatus.FAILED.value
                workflow.summary_result = f"Workflow halted at step '{step.name}': {error_msg}"
                db.commit()
                return workflow

        # -------------------------------------------------------------
        # STEP 3: Workflow Completion
        # -------------------------------------------------------------
        workflow.status = WorkflowStatus.COMPLETED.value
        workflow.completed_at = datetime.now(timezone.utc)
        workflow.summary_result = state.get("summary_result", "Workflow completed all steps successfully.")
        
        # Complete notification
        notif = Notification(
            title=f"Workflow Completed: {workflow.title}",
            message=f"All {len(steps)} agentic steps have completed successfully.",
            type="workflow_completed",
            user_id=user_id,
            link_url=f"/workflows/{workflow.id}"
        )
        db.add(notif)
        db.commit()

        return workflow

    @staticmethod
    async def resume_workflow(workflow_id: str, db: Session, reviewer_id: str, approved: bool) -> Workflow:
        """Resume execution of a workflow that was paused waiting for human approval."""
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found.")

        if not approved:
            workflow.status = WorkflowStatus.CANCELLED.value
            workflow.summary_result = "Workflow halted: Human reviewer rejected the pending sensitive action."
            db.commit()
            return workflow

        # Find the step that was waiting
        step = (
            db.query(WorkflowStep)
            .filter(WorkflowStep.workflow_id == workflow.id, WorkflowStep.status == StepStatus.WAITING_APPROVAL.value)
            .first()
        )
        if step:
            step.status = StepStatus.COMPLETED.value
            step.completed_at = datetime.now(timezone.utc)
            db.commit()

        # Continue remaining steps by running workflow
        return await Orchestrator.run_workflow(workflow_id, db, user_id=reviewer_id)
