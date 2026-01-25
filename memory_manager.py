"""
Memory Manager
Production-ready conversation memory + intent tracking
+ AI failure tracking + SLA timer
for Customer Support Agent
"""

from typing import List, Dict, Any
from datetime import datetime
from collections import Counter, deque


class MemoryManager:
    """
    Responsibilities:
    - Store user & agent messages
    - Enforce memory window
    - Provide formatted history for LLM
    - Track user intent patterns (refund, complaint, etc.)
    - Track failed AI replies (Step 4)
    - Track SLA time (auto escalation)
    """

    def __init__(self, max_history: int = 20, sla_seconds: int = 1800):
        """
        Args:
            max_history: Maximum number of messages to retain
            sla_seconds: SLA limit in seconds (default 30 minutes)
        """
        self.max_history = max_history
        self.sla_seconds = sla_seconds

        # =========================
        # Conversation memory
        # =========================
        self._history: List[Dict[str, Any]] = []

        # =========================
        # 🔁 Intent tracking (Step 3)
        # =========================
        self._intent_history = deque(maxlen=10)
        self._intent_counter = Counter()

        # =========================
        # 🔴 Failed AI reply tracking (Step 4)
        # =========================
        self.failed_ai_replies = 0

        # =========================
        # ⏱️ SLA tracking
        # =========================
        self.conversation_start = datetime.utcnow()

    # ==================================================
    # PUBLIC API
    # ==================================================

    def add_user_message(self, content: str) -> None:
        """Add user message + detect intent."""
        self._add_message(role="user", content=content)

        intent = self._detect_intent(content)
        self._intent_history.append(intent)
        self._intent_counter[intent] += 1

    def add_agent_message(self, content: str) -> None:
        """Add AI/agent message."""
        self._add_message(role="assistant", content=content)

    def get_history(self) -> List[Dict[str, Any]]:
        """Raw conversation history."""
        return list(self._history)

    def get_formatted_history(self) -> str:
        """Formatted history for LLM prompt."""
        return "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in self._history
        )

    def clear(self) -> None:
        """Clear all memory, intents, failure counters, and reset SLA."""
        self._history.clear()
        self._intent_history.clear()
        self._intent_counter.clear()
        self.failed_ai_replies = 0
        self.reset_sla()

    # ==================================================
    # 🔍 INTENT TRACKING (Step 3)
    # ==================================================

    def get_intent_count(self, intent: str) -> int:
        """How many times a specific intent occurred."""
        return self._intent_counter.get(intent, 0)

    def get_recent_intents(self) -> List[str]:
        """Recent intent history (debugging / analytics)."""
        return list(self._intent_history)

    # ==================================================
    # 🔴 FAILED AI REPLY TRACKING (Step 4)
    # ==================================================

    def mark_failed_ai_reply(self) -> None:
        """Increment failed AI reply counter."""
        self.failed_ai_replies += 1

    def reset_failed_ai_replies(self) -> None:
        """Reset failed AI reply counter."""
        self.failed_ai_replies = 0

    # ==================================================
    # ⏱️ SLA LOGIC
    # ==================================================

    def is_sla_breached(self) -> bool:
        """Check whether SLA time limit is exceeded."""
        elapsed = (datetime.utcnow() - self.conversation_start).total_seconds()
        return elapsed >= self.sla_seconds

    def reset_sla(self) -> None:
        """Reset SLA timer."""
        self.conversation_start = datetime.utcnow()

    # ==================================================
    # INTERNAL HELPERS
    # ==================================================

    def _add_message(self, role: str, content: str) -> None:
        """Internal method to add message and enforce memory window."""
        self._history.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        if len(self._history) > self.max_history:
            self._history.pop(0)

    def _detect_intent(self, message: str) -> str:
        """
        Lightweight intent classifier
        (Fast, explainable, production-friendly)
        """
        msg = message.lower()

        if "refund" in msg:
            if any(x in msg for x in ["want", "now", "immediately"]):
                return "REFUND_DEMAND"
            return "REFUND_INFO"

        if any(x in msg for x in ["complaint", "angry", "not happy", "bad", "worst"]):
            return "COMPLAINT"

        if any(x in msg for x in ["human", "agent", "support"]):
            return "HUMAN_REQUEST"

        return "GENERAL"
