"""
Customer Support Agent
- Short-term memory
- Long-term user memory
- Identity (name) handling
- RAG (knowledge base)
- Escalation + Admin dashboard
- Human takeover
"""

import logging
from datetime import datetime

from escalation_manager import EscalationManager
from memory_manager import MemoryManager
from tools import ToolRegistry
from vector_store import VectorStoreManager, UserMemoryStore
from admin_store import AdminStore
from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)


class CustomerSupportAgent:
    def __init__(self, user_id: str = "default_user"):
        # =========================
        # User Identity
        # =========================
        self.user_id = user_id

        # =========================
        # Core Components
        # =========================
        self.escalation_manager = EscalationManager()
        self.memory = MemoryManager(max_history=20, user_id=user_id)

        # =========================
        # Vector Stores
        # =========================
        self.vector_store_manager = VectorStoreManager()
        self.long_term_memory = UserMemoryStore(user_id)

        # =========================
        # Admin / Human takeover
        # =========================
        self.admin_store = AdminStore()
        self.human_takeover = False

        # =========================
        # Tools
        # =========================
        self.tools = ToolRegistry(self.vector_store_manager)

        # =========================
        # LLM
        # =========================
        self.llm = ChatOllama(
            model="llama3.2:1b",
            base_url="http://localhost:11434",
            temperature=0.2,
        )

        logger.info(
            f"CustomerSupportAgent initialized | user_id={user_id}"
        )

    # ==================================================
    # MAIN ENTRY
    # ==================================================

    def get_full_response(self, user_message: str) -> dict:
        logger.info(f"User message: {user_message}")

        # --------------------------------------------------
        # HUMAN TAKEOVER ACTIVE
        # --------------------------------------------------
        if self.human_takeover:
            return {
                "output": (
                    "🧑‍💼 A human support agent is handling your issue.\n"
                    "Please wait for their response."
                ),
                "escalated": True,
            }

        # --------------------------------------------------
        # STEP 1: NAME EXTRACTION (FAST PATH)
        # --------------------------------------------------
        name = self.memory.extract_name(user_message)
        if name:
            # store name in long-term memory
            self.long_term_memory.add_memory(
                text=f"User name is {name}",
                metadata={
                    "type": "identity",
                    "field": "name",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            reply = f"Nice to meet you, {name} 🙂"
            self.memory.add_agent_message(reply)

            return {
                "output": reply,
                "escalated": False,
            }

        # --------------------------------------------------
        # STEP 2: NAME RECALL (Do you remember my name?)
        # --------------------------------------------------
        if self._is_name_question(user_message):
            memories = self.long_term_memory.get_relevant_memory(
                "user name", k=1
            )

            if memories:
                stored = memories[0].page_content.replace(
                    "User name is ", ""
                )
                reply = f"Yes 🙂 I remember your name. Your name is **{stored}**."
            else:
                reply = "You haven't told me your name yet 🙂"

            self.memory.add_agent_message(reply)
            return {
                "output": reply,
                "escalated": False,
            }

        # --------------------------------------------------
        # STEP 3: SAVE MESSAGE + INTENT
        # --------------------------------------------------
        intent = self.memory.add_user_message(user_message)

        # store important things only
        if self.memory.should_store_long_term(intent):
            self.long_term_memory.add_memory(
                text=self.memory.extract_memory_text(user_message),
                metadata={
                    "intent": intent,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        # --------------------------------------------------
        # STEP 4: REPEATED INTENT ESCALATION
        # --------------------------------------------------
        if (
            self.memory.get_intent_count("REFUND_DEMAND") >= 2
            or self.memory.get_intent_count("COMPLAINT") >= 2
        ):
            return {
                "output": self._handle_escalation(
                    user_message,
                    "Repeated complaint or refund demand",
                    "HIGH",
                ),
                "escalated": True,
            }

        # --------------------------------------------------
        # STEP 5: KEYWORD ESCALATION
        # --------------------------------------------------
        decision = self.escalation_manager.should_escalate(user_message)
        if decision.get("level") == "HIGH":
            return {
                "output": self._handle_escalation(
                    user_message,
                    decision["reason"],
                    self._decide_priority(decision["reason"]),
                ),
                "escalated": True,
            }

        # --------------------------------------------------
        # STEP 6: SMALL TALK
        # --------------------------------------------------
        if user_message.lower().strip() in [
            "hi",
            "hello",
            "hey",
            "how are you",
        ]:
            reply = self.llm.invoke(user_message).content.strip()
            self.memory.add_agent_message(reply)
            return {"output": reply, "escalated": False}

        # --------------------------------------------------
        # STEP 7: LONG-TERM MEMORY CONTEXT
        # --------------------------------------------------
        past_memories = self.long_term_memory.get_relevant_memory(
            user_message, k=3
        )

        memory_context = ""
        if past_memories:
            memory_context = "\n".join(
                f"- {m.page_content}" for m in past_memories
            )

        # --------------------------------------------------
        # STEP 8: RAG
        # --------------------------------------------------
        documents = []
        store = self.vector_store_manager.get_vector_store()
        if store:
            documents = store.similarity_search(user_message, k=3)

        kb_context = "\n\n".join(
            doc.page_content for doc in documents
        )

        prompt = f"""
You are a professional customer support AI.

Known information about this user:
{memory_context}

Conversation history:
{self.memory.get_formatted_history()}

Knowledge base info:
{kb_context}

User question:
{user_message}

Answer clearly and politely.
"""

        answer = self.llm.invoke(prompt).content.strip()
        self.memory.add_agent_message(answer)

        return {
            "output": answer,
            "escalated": False,
            "source_documents": documents,
        }

    # ==================================================
    # ESCALATION
    # ==================================================

    def _handle_escalation(
        self, message: str, reason: str, priority: str
    ) -> str:
        ticket = self.tools.get_tool("ticket").run(
            user_message=message,
            reason=reason,
            priority=priority,
        )

        self.admin_store.add_escalation(
            ticket_id=ticket["ticket_id"],
            user_id=self.user_id,
            reason=reason,
            priority=priority,
            conversation=self.memory.get_history(),
        )

        self.human_takeover = True

        reply = (
            "🚨 **This issue requires human assistance**\n\n"
            f"**Reason:** {reason}\n"
            f"**Priority:** {priority}\n\n"
            f"🎫 **Ticket ID:** {ticket['ticket_id']}"
        )

        self.memory.add_agent_message(reply)
        return reply

    # ==================================================
    # HELPERS
    # ==================================================

    def clear_memory(self):
        self.memory.clear()
        self.human_takeover = False

    def _decide_priority(self, reason: str) -> str:
        reason = reason.lower()
        if any(x in reason for x in ["fraud", "scam", "hacked"]):
            return "HIGH"
        if any(x in reason for x in ["refund", "billing", "payment"]):
            return "MEDIUM"
        return "MEDIUM"

    def _is_name_question(self, message: str) -> bool:
        msg = message.lower()
        return any(
            x in msg
            for x in [
                "my name",
                "remember my name",
                "what is my name",
                "amar naam",
                "amar nam ki",
            ]
        )
