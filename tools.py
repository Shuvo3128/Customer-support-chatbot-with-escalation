"""
Tools Module
Defines all actions the customer support agent can perform
"""

from typing import Dict, List
from datetime import datetime
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
import config
import logging

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
# Ticket Creation Tool (STEP 5 🔥)
# =========================

class TicketTool:
    name = "ticket"
    description = "Create a support ticket for human agents"

    def run(self, user_message: str, reason: str, priority: str) -> Dict:
        """
        priority: LOW / MEDIUM / HIGH
        """
        return {
            "ticket_id": self._generate_ticket_id(),
            "issue": user_message,
            "reason": reason,
            "priority": priority,     # ✅ STEP 5
            "status": "OPEN",
            "created_at": datetime.utcnow().isoformat(),
        }

    def _generate_ticket_id(self) -> str:
        return f"TICKET-{int(datetime.utcnow().timestamp())}"


# =========================
# Escalation Helper Tool (STEP 5 🔥)
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
# Knowledge Base Search Tool (WITH LLM AUTO SUMMARY)
# =========================

class KnowledgeBaseSearchTool:
    name = "kb_search"
    description = "Search and summarize the knowledge base"

    def __init__(self, vector_store_manager):
        self.vector_store_manager = vector_store_manager
        self.llm = ChatOllama(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0.2,
        )

    def run(self, query: str) -> str:
        vector_store = self.vector_store_manager.get_vector_store()

        if vector_store is None:
            return (
                "The knowledge base is not ready yet. "
                "Please load documents first."
            )

        # 1️⃣ Similarity search
        results: List[Document] = vector_store.similarity_search(query, k=3)

        # 2️⃣ No result → intelligent summary
        if not results:
            return self._auto_summarize(query)

        # 3️⃣ Normal KB answer
        response = "📄 **Here’s what I found in the knowledge base:**\n\n"
        for doc in results:
            source = doc.metadata.get("source", "Unknown document")
            page = doc.metadata.get("page", "N/A")
            response += (
                f"- {doc.page_content[:300]}...\n"
                f"  _(Source: {source}, Page: {page})_\n\n"
            )

        return response.strip()

    # =========================
    # AUTO SUMMARY USING LLM
    # =========================

    def _auto_summarize(self, query: str) -> str:
        prompt = f"""
You are a professional customer support assistant.

The user asked:
"{query}"

The knowledge base does not contain a direct answer.
Provide a helpful, polite, high-level explanation
based on typical customer support documentation.
"""
        response = self.llm.invoke(prompt)
        return response.content.strip()


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
