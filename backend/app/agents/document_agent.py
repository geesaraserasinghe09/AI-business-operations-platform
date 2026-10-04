import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.agents.state import AgentState
from app.agents.tools import DocumentTools
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

DOCUMENT_SYSTEM_PROMPT = """
You are the Enterprise Document Analysis Agent. You specialize in RAG (Retrieval-Augmented Generation),
extracting key terms, policies, compliance guidelines, and contract clauses from enterprise documentation.
"""


class DocumentAgent:
    """Specialized agent responsible for document parsing, semantic RAG search, and policy summarization."""

    @staticmethod
    async def execute(state: AgentState, db: Session) -> AgentState:
        prompt = state.get("prompt", "")
        logger.info(f"[DocumentAgent] Executing document RAG retrieval for: {prompt[:60]}...")

        # 1. Retrieve top matching chunks from uploaded documents
        matched_chunks = DocumentTools.search_documents(db, prompt, top_k=4)

        if not matched_chunks:
            context_text = "No uploaded internal documents matched the query keywords."
        else:
            context_text = "\n\n---\n\n".join([f"Source Chunk [{c['chunk_id'][:8]}]:\n{c['content']}" for c in matched_chunks])

        # 2. Synthesize document analysis
        analysis_prompt = (
            f"User Goal: {prompt}\n\n"
            f"Retrieved Document Context:\n{context_text}\n\n"
            f"Synthesize key operational guidelines, policies, or relevant clauses found in the documentation."
        )

        schema = """
        {
          "summary": "string (executive summary of retrieved documentation)",
          "key_clauses": ["string"],
          "compliance_notes": "string",
          "matched_count": 0
        }
        """

        structured_result = await llm_service.generate_structured(
            prompt=analysis_prompt,
            schema_description=schema,
            system_instruction=DOCUMENT_SYSTEM_PROMPT
        )

        result_payload = {
            "summary": structured_result.get("summary", "Document context analyzed."),
            "relevant_chunks": [c["content"] for c in matched_chunks],
            "key_clauses": structured_result.get("key_clauses", []),
            "compliance_notes": structured_result.get("compliance_notes", "Standard operational procedures apply.")
        }

        state.setdefault("agent_outputs", {})["document"] = result_payload
        return state
