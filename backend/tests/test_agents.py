import pytest
from app.agents.state import AgentState
from app.agents.planner_agent import PlannerAgent
from app.agents.reporting_agent import ReportingAgent


@pytest.mark.asyncio
async def test_planner_agent_decomposition():
    state: AgentState = {
        "prompt": "Analyze this month's sales, identify top products, and summarize unresolved customer tickets.",
        "steps": [],
        "agent_outputs": {},
        "current_step_index": 0
    }

    result_state = await PlannerAgent.plan(state)
    assert "plan" in result_state
    tasks = result_state["plan"].get("tasks", [])
    assert len(tasks) > 0

    agent_types = [t["agent_type"] for t in tasks]
    assert "finance" in agent_types or "support" in agent_types or "reporting" in agent_types


@pytest.mark.asyncio
async def test_reporting_agent_synthesis():
    state: AgentState = {
        "prompt": "Prepare monthly ops summary",
        "agent_outputs": {
            "finance": {
                "summary": "Revenue up 14%",
                "metrics": {"total_revenue": 450000.0}
            },
            "support": {
                "summary": "12 open tickets",
                "stats": {"open_tickets": 12}
            }
        }
    }

    result = await ReportingAgent.execute(state)
    assert "reporting" in result["agent_outputs"]
    report = result["agent_outputs"]["reporting"]
    assert "summary" in report
    assert "markdown_content" in report
    assert len(report["markdown_content"]) > 20
