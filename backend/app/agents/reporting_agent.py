import logging
from typing import Dict, Any
from app.agents.state import AgentState
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

REPORTING_SYSTEM_PROMPT = """
You are the Enterprise Reporting Agent. You synthesize cross-functional business intelligence
from Finance, Customer Support, and Document Agents into an authoritative, publication-ready
Executive Briefing Report with clear KPIs, risk assessments, and strategic recommendations.
"""


class ReportingAgent:
    """Specialized agent responsible for cross-functional data synthesis and report generation."""

    @staticmethod
    async def execute(state: AgentState) -> AgentState:
        prompt = state.get("prompt", "")
        outputs = state.get("agent_outputs", {})
        logger.info(f"[ReportingAgent] Synthesizing final report for: {prompt[:60]}...")

        finance_data = outputs.get("finance", {})
        support_data = outputs.get("support", {})
        document_data = outputs.get("document", {})

        synthesis_prompt = (
            f"Original Request: {prompt}\n\n"
            f"Finance Agent Intelligence:\n{finance_data}\n\n"
            f"Customer Support Agent Intelligence:\n{support_data}\n\n"
            f"Document Agent Intelligence:\n{document_data}\n\n"
            f"Generate a comprehensive, executive-ready Operations Briefing Report in Markdown format. "
            f"Include an Executive Summary, Key Metrics Table, Critical Incidents & Risks, "
            f"and Strategic Next Steps."
        )

        schema = """
        {
          "report_title": "string (executive report title)",
          "executive_summary": "string (high-level synthesis)",
          "markdown_content": "string (full multi-section formatted report)",
          "action_items": ["string"]
        }
        """

        structured_result = await llm_service.generate_structured(
            prompt=synthesis_prompt,
            schema_description=schema,
            system_instruction=REPORTING_SYSTEM_PROMPT
        )

        final_summary = structured_result.get("executive_summary", "Business operations workflow completed successfully.")
        full_markdown = structured_result.get("markdown_content", "")
        if not full_markdown or len(full_markdown) < 50:
            sections = [
                f"# {structured_result.get('report_title', 'Executive Business Operations Report')}\n",
                f"**Request:** {prompt}\n",
                f"## Executive Summary\n{final_summary}\n"
            ]

            if document_data:
                doc_summary = document_data.get("summary", "Document intelligence extracted.")
                sections.append(f"## Document Intelligence & Analysis\n{doc_summary}\n")
                if document_data.get("key_clauses"):
                    sections.append("### Key Findings & Highlights")
                    sections.extend([f"- {clause}" for clause in document_data["key_clauses"]])
                    sections.append("")
                if document_data.get("relevant_chunks"):
                    sections.append("### Key Source Excerpts")
                    for i, chunk in enumerate(document_data["relevant_chunks"][:2]):
                        clean_chunk = chunk.strip().replace("\n", " ")[:300]
                        sections.append(f"> \"{clean_chunk}...\"\n")

            if finance_data:
                sections.append(
                    f"## Financial Performance Highlights\n"
                    f"- **Total Revenue:** ${finance_data.get('metrics', {}).get('total_revenue', 0.0):,.2f}\n"
                    f"- **Top Product:** {finance_data.get('top_products', [{}])[0].get('name', 'N/A')}\n"
                    f"- **Anomalies Identified:** {len(finance_data.get('anomalies', []))} detected\n"
                )

            if support_data:
                sections.append(
                    f"## Customer Support Health\n"
                    f"- **Open Tickets:** {support_data.get('stats', {}).get('open_tickets', 0)}\n"
                    f"- **Urgent Escalations:** {len(support_data.get('urgent_cases', []))}\n"
                )

            actions = structured_result.get("action_items", [])
            if not actions:
                actions = ["Review operational intelligence report", "Follow up on identified business action items"]
            sections.append("## Recommended Action Items")
            sections.extend([f"- {item}" for item in actions])

            full_markdown = "\n".join(sections)

        result_payload = {
            "title": structured_result.get("report_title", "Executive Business Operations Briefing"),
            "summary": final_summary,
            "markdown_content": full_markdown,
            "action_items": structured_result.get("action_items", []),
            "metadata": {
                "finance_included": bool(finance_data),
                "support_included": bool(support_data),
                "document_included": bool(document_data)
            }
        }

        state.setdefault("agent_outputs", {})["reporting"] = result_payload
        state["summary_result"] = final_summary
        return state
