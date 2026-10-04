import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.agents.state import AgentState
from app.agents.tools import SupportTools
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

SUPPORT_SYSTEM_PROMPT = """
You are the Enterprise Customer Support Agent. You evaluate support ticket backlogs,
cluster customer complaints, determine severity priorities, suggest response drafts,
and identify tickets requiring executive escalation.
"""


class SupportAgent:
    """Specialized agent responsible for customer ticket analysis, sentiment classification, and escalation routing."""

    @staticmethod
    async def execute(state: AgentState, db: Session) -> AgentState:
        prompt = state.get("prompt", "")
        logger.info(f"[SupportAgent] Executing support analysis for: {prompt[:60]}...")

        # 1. Retrieve support ticket metrics using scoped tool
        ticket_data = SupportTools.get_support_tickets_summary(db)

        # 2. Analyze tickets and sentiment
        analysis_prompt = (
            f"User Goal: {prompt}\n\n"
            f"Ticket Backlog Snapshot:\n"
            f"- Total Tickets: {ticket_data['total_tickets']}\n"
            f"- Open Tickets: {ticket_data['open_tickets']}\n"
            f"- Urgent/High Priority: {ticket_data['urgent_tickets']}\n"
            f"- Category Distribution: {ticket_data['category_distribution']}\n"
            f"- Sample Unresolved Complaints: {ticket_data['unresolved_tickets']}\n\n"
            f"Categorize the primary root causes, summarize key complaints, recommend automated draft replies, "
            f"and indicate if urgent tickets should be escalated."
        )

        schema = """
        {
          "summary": "string (support backlog overview)",
          "complaint_clusters": [{"category": "string", "count": 0, "root_cause": "string"}],
          "urgent_cases": [{"ticket_number": "string", "issue": "string", "recommended_action": "string"}],
          "suggested_response_draft": "string",
          "requires_escalation": false
        }
        """

        structured_result = await llm_service.generate_structured(
            prompt=analysis_prompt,
            schema_description=schema,
            system_instruction=SUPPORT_SYSTEM_PROMPT
        )

        result_payload = {
            "summary": structured_result.get("summary", "Support ticket analysis completed."),
            "stats": ticket_data,
            "complaint_clusters": structured_result.get("complaint_clusters", []),
            "urgent_cases": structured_result.get("urgent_cases", []),
            "suggested_response": structured_result.get("suggested_response_draft", ""),
        }

        # Check if sensitive action is required (e.g. escalating ticket or sending automated customer email)
        if any(w in prompt.lower() for w in ["escalate", "send email", "notify customer", "alert client"]) or ticket_data.get("urgent_tickets", 0) > 0:
            state["approval_required"] = True
            state["approval_payload"] = {
                "action_type": "customer_escalation_and_email",
                "title": "Approve Customer Escalation & Official Communication",
                "description": "Customer Support Agent identified high-priority customer ticket requiring executive dispatch.",
                "reason": "Enterprise client SLA breach risk detected on Ticket #TK-8402 (API integration outage).",
                "ai_explanation": "Customer is blocked on production checkout. Automated escalation email drafted with priority SLA tier response.",
                "data_payload": {
                    "ticket_number": "TK-8402",
                    "recipient": "cto@acmecorp.com",
                    "subject": "[CRITICAL] Update regarding Enterprise API Integration Outage",
                    "email_body": structured_result.get("suggested_response_draft", "We have escalated this issue to tier-3 engineering with immediate priority.")
                },
                "agent_name": "Customer Support Agent",
                "risk_level": "critical"
            }

        state.setdefault("agent_outputs", {})["support"] = result_payload
        return state
