import logging
from typing import Dict, Any
from app.services.llm_service import llm_service
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """
You are the Task Planning Agent in an Enterprise AI Business Operations Platform.
Your mission is to analyze natural language business requests and break them down into an efficient,
ordered execution graph of specialized tasks with appropriate agent assignments.

Available specialized agents:
- 'finance': Analyzes sales records, revenue, product performance, and financial anomalies.
- 'support': Analyzes customer tickets, complaint categories, sentiment, and resolution escalations.
- 'document': Performs RAG retrieval, document summarization, and policy checks.
- 'reporting': Combines multi-agent findings into structured management briefings and KPI summaries.

Rules:
1. Break down requests into clear, non-overlapping steps.
2. If any step involves sensitive actions (e.g. sending emails, issuing refunds, modifying records, deleting data, escalating high-risk accounts), mark 'requires_approval': true.
3. Order tasks logically so dependent tasks execute after their prerequisites.
4. Reporting agent should typically run last to synthesize all findings.
"""

SCHEMA_DESC = """
{
  "workflow_title": "string (concise descriptive title)",
  "summary": "string (brief description of planned execution)",
  "tasks": [
    {
      "step_order": 1,
      "name": "string (task title)",
      "agent_type": "finance | support | document | reporting",
      "description": "string (what the agent must accomplish)",
      "requires_approval": false
    }
  ]
}
"""


class PlannerAgent:
    """Specialized agent responsible for decomposing business requests into actionable multi-agent plans."""

    @staticmethod
    async def plan(state: AgentState) -> AgentState:
        prompt = state.get("prompt", "")
        logger.info(f"[PlannerAgent] Planning execution for prompt: {prompt[:60]}...")

        plan = await llm_service.generate_structured(
            prompt=f"Create a multi-agent business operations plan for this request:\n\n'{prompt}'",
            schema_description=SCHEMA_DESC,
            system_instruction=PLANNER_SYSTEM_PROMPT
        )

        tasks = plan.get("tasks", [])
        state["plan"] = plan
        state["steps"] = tasks
        state["current_step_index"] = 0
        state["agent_outputs"] = state.get("agent_outputs", {})
        state["agent_outputs"]["planner"] = plan

        return state
