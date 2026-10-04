from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict, total=False):
    """LangGraph state representation flowing through all nodes."""
    workflow_id: str
    user_id: Optional[str]
    prompt: str
    plan: Dict[str, Any]
    steps: List[Dict[str, Any]]
    current_step_index: int
    agent_outputs: Dict[str, Any]
    approval_required: bool
    approval_payload: Optional[Dict[str, Any]]
    is_paused_for_human: bool
    summary_result: Optional[str]
    errors: List[str]
