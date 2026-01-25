"""
Customer Support Agent
Handles escalation, memory, intent-awareness, tools, and LLM responses
"""

import logging
from escalation_manager import EscalationManager
from memory_manager import MemoryManager
from tools import ToolRegistry
from vector_store import VectorStoreManager
from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)


class CustomerSupportAgent:
    def __init__(self):
        # =========================
        # Core Components
        # =========================
        self.escalation_manager = EscalationManager()
        self.memory = MemoryManager(max_history=20)

        # =========================
        # Vector Store Manager
        # =========================
        self.vector_store_manager = VectorStoreManager()

        # =========================
        # Tools
        # =========================
        self.tools = ToolRegistry(self.vector_store_manager)

        # =========================
        # LLM (Ollama)
        # =========================
        self.llm = ChatOllama(
            model="llama3.2:1b",
            base_url="http://localhost:11434",
            temperature=0.2,
        )

        logger.info("CustomerSupportAgent initialized successfully")

    # ==================================================
    # MAIN ENTRY (Used by app.py)
    # ==================================================

    def get_full_response(self, user_message: str) -> dict:
        logger.info(f"User message received: {user_message}")

        # ==================================================
        # STEP 1 — Save user message + intent tracking
        # ==================================================
        self.memory.add_user_message(user_message)

        # ==================================================
        # STEP 3 — Repeated intent detection
        # ==================================================
        refund_demand_count = self.memory.get_intent_count("REFUND_DEMAND")
        complaint_count = self.memory.get_intent_count("COMPLAINT")

        if refund_demand_count >= 2 or complaint_count >= 2:
            response = self._handle_escalation(
                message=user_message,
                reason="Repeated complaint or refund demand detected",
                priority="HIGH",
            )
            return {
                "output": response,
                "escalated": True,
            }

        # ==================================================
        # STEP 2 — Pattern-based escalation (FIXED 🔥)
        # ==================================================
        decision = self.escalation_manager.should_escalate(user_message)

        if decision["level"] == "HIGH":
            priority = self._decide_priority(decision["reason"])

            response = self._handle_escalation(
                message=user_message,
                reason=decision["reason"],
                priority=priority,
            )
            return {
                "output": response,
                "escalated": True,
            }

        # ==================================================
        # STEP 4 — AI response
        # ==================================================
        ai_response = self._handle_with_llm(user_message)

        # ==================================================
        # STEP 4 — Auto escalation after failed AI replies
        # ==================================================
        failure_indicators = [
            "i don't know",
            "not sure",
            "cannot help",
            "no information",
            "don't have information",
            "knowledge base is not ready",
            "please provide more context",
        ]

        if any(x in ai_response.lower() for x in failure_indicators):
            self.memory.mark_failed_ai_reply()
            logger.warning(
                f"AI failure detected ({self.memory.failed_ai_replies})"
            )
        else:
            self.memory.reset_failed_ai_replies()

        if self.memory.failed_ai_replies >= 3:
            response = self._handle_escalation(
                message=user_message,
                reason="Multiple failed AI responses",
                priority="HIGH",
            )
            return {
                "output": response,
                "escalated": True,
            }

        # ==================================================
        # Save AI response
        # ==================================================
        self.memory.add_agent_message(ai_response)

        return {
            "output": ai_response,
            "escalated": False,
        }

    # ==================================================
    # ESCALATION FLOW (STEP 5)
    # ==================================================

    def _handle_escalation(self, message: str, reason: str, priority: str) -> str:
        ticket_tool = self.tools.get_tool("ticket")
        escalation_tool = self.tools.get_tool("escalation")

        ticket = ticket_tool.run(
            user_message=message,
            reason=reason,
            priority=priority,
        )

        summary = escalation_tool.run(
            user_message=message,
            reason=reason,
            priority=priority,
        )

        response = (
            "🚨 **This issue requires human assistance**\n\n"
            f"**Reason:** {reason}\n"
            f"**Priority:** {priority}\n\n"
            f"{summary}\n\n"
            f"🎫 **Ticket ID:** {ticket['ticket_id']}"
        )

        self.memory.add_agent_message(response)
        return response

    # ==================================================
    # LLM + KNOWLEDGE BASE
    # ==================================================

    def _handle_with_llm(self, message: str) -> str:
        kb_tool = self.tools.get_tool("kb_search")
        kb_result = kb_tool.run(message)

        context = ""
        if kb_result:
            context = f"\n\nRelevant knowledge base info:\n{kb_result}"

        prompt = f"""
You are a professional, calm, and helpful customer support AI.

Conversation history:
{self.memory.get_formatted_history()}

User question:
{message}

{context}

Respond clearly and politely.
"""

        response = self.llm.invoke(prompt)
        return response.content.strip()

    # ==================================================
    # UTILITIES
    # ==================================================

    def clear_memory(self) -> None:
        self.memory.clear()
        logger.info("Conversation memory cleared")

    # ==================================================
    # INTERNAL HELPERS
    # ==================================================

    def _decide_priority(self, reason: str) -> str:
        """
        Decide ticket priority based on escalation reason
        """
        reason_lower = reason.lower()

        if any(x in reason_lower for x in ["complaint", "fraud", "scam", "hacked"]):
            return "HIGH"

        if any(x in reason_lower for x in ["refund", "payment", "billing"]):
            return "MEDIUM"

        return "LOW"
