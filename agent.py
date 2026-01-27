"""
Customer Support Agent
Handles escalation, memory, intent-awareness, tools, and LLM responses
(Fixed Full RAG-enabled version)
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
        # Vector Store Manager (RAG)
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
    # MAIN ENTRY
    # ==================================================

    def get_full_response(self, user_message: str) -> dict:
        logger.info(f"User message received: {user_message}")

        # Save user message + intent tracking
        self.memory.add_user_message(user_message)

        # ==================================================
        # STEP 1 — Repeated intent detection
        # ==================================================
        if (
            self.memory.get_intent_count("REFUND_DEMAND") >= 2
            or self.memory.get_intent_count("COMPLAINT") >= 2
        ):
            response = self._handle_escalation(
                message=user_message,
                reason="Repeated complaint or refund demand detected",
                priority="HIGH",
            )
            return {"output": response, "escalated": True}

        # ==================================================
        # STEP 2 — Pattern-based escalation
        # ==================================================
        decision = self.escalation_manager.should_escalate(user_message)

        if decision.get("level") == "HIGH":
            response = self._handle_escalation(
                message=user_message,
                reason=decision["reason"],
                priority=self._decide_priority(decision["reason"]),
            )
            return {"output": response, "escalated": True}

        # ==================================================
        # STEP 3 — Small talk bypass (IMPORTANT FIX)
        # ==================================================
        small_talk = ["hi", "hello", "hey", "how are you"]
        if user_message.lower().strip() in small_talk:
            response = self.llm.invoke(user_message).content.strip()
            self.memory.add_agent_message(response)
            return {"output": response, "escalated": False}

        # ==================================================
        # STEP 4 — RAG: Retrieve documents
        # ==================================================
        vector_store = self.vector_store_manager.get_vector_store()
        documents = []

        if vector_store:
            documents = vector_store.similarity_search(user_message, k=3)

        # Build context from documents
        context = ""
        if documents:
            context = "\n\n".join(doc.page_content for doc in documents)

        # ==================================================
        # STEP 5 — LLM Answer using RAG context
        # ==================================================
        prompt = f"""
You are a professional customer support AI.

Conversation history:
{self.memory.get_formatted_history()}

User question:
{user_message}

Relevant knowledge base information:
{context}

Answer clearly and politely.
"""

        answer = self.llm.invoke(prompt).content.strip()

        # ==================================================
        # STEP 6 — Auto escalation after failed AI replies
        # ==================================================
        failure_indicators = [
            "i don't know",
            "not sure",
            "cannot help",
            "no information",
            "don't have information",
        ]

        if any(x in answer.lower() for x in failure_indicators):
            self.memory.mark_failed_ai_reply()
        else:
            self.memory.reset_failed_ai_replies()

        if self.memory.failed_ai_replies >= 3:
            response = self._handle_escalation(
                message=user_message,
                reason="Multiple failed AI responses",
                priority="HIGH",
            )
            return {"output": response, "escalated": True}

        # Save response
        self.memory.add_agent_message(answer)

        return {
            "output": answer,
            "escalated": False,
            "source_documents": documents,  # ✅ RAG SOURCES
        }

    # ==================================================
    # ESCALATION FLOW
    # ==================================================

    def _handle_escalation(self, message: str, reason: str, priority: str) -> str:
        ticket = self.tools.get_tool("ticket").run(
            user_message=message,
            reason=reason,
            priority=priority,
        )

        summary = self.tools.get_tool("escalation").run(
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
    # UTILITIES
    # ==================================================

    def clear_memory(self) -> None:
        self.memory.clear()
        logger.info("Conversation memory cleared")

    def _decide_priority(self, reason: str) -> str:
        reason = reason.lower()
        if any(x in reason for x in ["complaint", "fraud", "scam", "hacked"]):
            return "HIGH"
        if any(x in reason for x in ["refund", "billing", "payment"]):
            return "MEDIUM"
        return "LOW"
