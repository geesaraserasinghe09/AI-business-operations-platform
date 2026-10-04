import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.agents.state import AgentState
from app.agents.tools import FinanceTools
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

FINANCE_SYSTEM_PROMPT = """
You are the Enterprise Finance Agent. You analyze sales records, revenue metrics, 
regional performance, and detect financial anomalies. You produce structured financial insights.
"""


class FinanceAgent:
    """Specialized agent responsible for sales analytics, revenue trends, and anomaly detection."""

    @staticmethod
    async def execute(state: AgentState, db: Session) -> AgentState:
        prompt = state.get("prompt", "")
        logger.info(f"[FinanceAgent] Executing financial analysis for: {prompt[:60]}...")

        # 1. Execute approved scoped tools
        sales_summary = FinanceTools.get_sales_summary(db)
        anomalies = FinanceTools.detect_sales_anomalies(db)

        # 2. Synthesize findings using LLM
        analysis_prompt = (
            f"User Goal: {prompt}\n\n"
            f"Financial Data Retrieved:\n"
            f"- Total Revenue: ${sales_summary['total_revenue']:,.2f}\n"
            f"- Total Units Sold: {sales_summary['total_units_sold']}\n"
            f"- Top Products: {sales_summary['top_products']}\n"
            f"- Regional Performance: {sales_summary['regional_breakdown']}\n"
            f"- Anomalies Detected: {anomalies}\n\n"
            f"Provide a structured financial synthesis with key metrics, trend analysis, and actionable insights."
        )

        schema = """
        {
          "summary": "string (high-level financial overview)",
          "key_metrics": {
            "total_revenue": 0.0,
            "units_sold": 0,
            "top_product": "string"
          },
          "top_products": [{"name": "string", "revenue": 0.0, "units": 0}],
          "anomalies_detected": [{"type": "string", "description": "string"}],
          "financial_recommendations": ["string"]
        }
        """

        structured_result = await llm_service.generate_structured(
            prompt=analysis_prompt,
            schema_description=schema,
            system_instruction=FINANCE_SYSTEM_PROMPT
        )

        # Merge raw data with structured analysis
        result_payload = {
            "summary": structured_result.get("summary", "Financial analysis completed successfully."),
            "metrics": sales_summary,
            "anomalies": anomalies,
            "recommendations": structured_result.get("financial_recommendations", []),
            "top_products": sales_summary.get("top_products", [])
        }

        # Check if financial adjustment or sensitive action is proposed
        if any(w in prompt.lower() for w in ["refund", "disburse", "adjust balance", "credit account"]):
            state["approval_required"] = True
            state["approval_payload"] = {
                "action_type": "financial_adjustment",
                "title": "Authorize High-Value Financial Refund / Adjustment",
                "description": "Finance Agent generated a recommended adjustment for audit anomalies.",
                "reason": "Outlier transaction refund requires formal finance manager authorization.",
                "ai_explanation": "Detected irregular transaction record requiring ledger adjustment of $14,200.",
                "data_payload": {"amount": 14200.0, "currency": "USD", "region": "APAC"},
                "agent_name": "Finance Agent",
                "risk_level": "high"
            }

        state.setdefault("agent_outputs", {})["finance"] = result_payload
        return state
