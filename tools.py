"""
Tools Module
Defines all actions the customer support agent can perform
(Fully RAG-compatible)
"""

from typing import Dict, List
from datetime import datetime
import logging

from langchain_core.documents import Document
from langchain_ollama import ChatOllama

import config

logger = logging.getLogger(__name__)

# =========================
# Calculator Tool
# =========================

class CalculatorTool:
    name = "calculator"
    description = "Perform basic mathematical calculations"

    def run(self, expression: str) -> str:
        try:
            expression = expression.lower().replace("calculate", "").strip()
            result = eval(expression, {"__builtins__": {}})
            return f"Result: {result}"
        except Exception:
            return "Sorry, I could not calculate that."


# =========================
# Ticket Creation Tool (STEP 5)
# =========================

class TicketTool:
    name = "ticket"
    description = "Create a support ticket for human agents"

    def run(self, user_message: str, reason: str, priority: str) -> Dict:
        return {
            "ticket_id": self._generate_ticket_id(),
            "issue": user_message,
            "reason": reason,
            "priority": priority,
            "status": "OPEN",
            "created_at": datetime.utcnow().isoformat(),
        }

    def _generate_ticket_id(self) -> str:
        return f"TICKET-{int(datetime.utcnow().timestamp())}"


# =========================
# Escalation Helper Tool
# =========================

class EscalationTool:
    name = "escalation"
    description = "Prepare escalation summary for human agent"

    def run(self, user_message: str, reason: str, priority: str) -> str:
        return (
            "Escalation Summary:\n"
            f"- Issue: {user_message}\n"
            f"- Reason: {reason}\n"
            f"- Priority: {priority}\n"
            "This case requires human assistance."
        )


# =========================
# Knowledge Base Search Tool (FULL RAG ✅)
# =========================

class KnowledgeBaseSearchTool:
    """
    RAG Tool:
    - Retrieves documents from vector DB
    - Generates answer ONLY from retrieved context
    - Returns answer + source documents
    """

    name = "kb_search"
    description = "Search the knowledge base using Retrieval-Augmented Generation"

    def __init__(self, vector_store_manager):
        self.vector_store_manager = vector_store_manager
        self.llm = ChatOllama(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0.2,
        )

    def run(self, query: str) -> Dict:
        vector_store = self.vector_store_manager.get_vector_store()

        # ❌ KB not ready
        if vector_store is None:
            return {
                "answer": (
                    "The knowledge base is not ready yet. "
                    "Please load documents first."
                ),
                "source_documents": [],
            }

        # 🔍 Retrieve documents
        docs: List[Document] = vector_store.similarity_search(query, k=4)

        if not docs:
            return {
                "answer": (
                    "I could not find relevant information in the knowledge base. "
                    "Please contact support if this issue is critical."
                ),
                "source_documents": [],
            }

        # 🧠 Build strict RAG prompt
        context = "\n\n".join(
            f"[Source: {d.metadata.get('source', 'Unknown')} | "
            f"Page: {d.metadata.get('page', 'N/A')}]\n"
            f"{d.page_content}"
            for d in docs
        )

        prompt = f"""
You are a professional customer support AI.

Answer the question using ONLY the context below.
If the answer is not present, say "I don't know".

Context:
{context}

Question:
{query}

Answer:
"""

        response = self.llm.invoke(prompt)

        return {
            "answer": response.content.strip(),
            "source_documents": docs,
        }


# =========================
# Tool Registry
# =========================

class ToolRegistry:
    """
    Central place to manage and access all tools
    """

    def __init__(self, vector_store_manager):
        self.tools = {
            "calculator": CalculatorTool(),
            "ticket": TicketTool(),
            "escalation": EscalationTool(),
            "kb_search": KnowledgeBaseSearchTool(vector_store_manager),
        }

        logger.info("ToolRegistry initialized")

    def get_tool(self, name: str):
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.keys())
