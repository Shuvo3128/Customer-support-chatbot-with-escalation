"""
Memory Manager
Production-ready conversation memory + intent tracking
+ AI failure tracking + SLA timer
+ Long-Term Memory hooks
+ ⚡ Identity Fast-Path (Strong Name Handling)
"""

from typing import List, Dict, Any
from datetime import datetime
from collections import Counter, deque
import re


class MemoryManager:
    """
    Responsibilities:
    - Store user & agent messages
    - Enforce memory window
    - Provide formatted history for LLM
    - Track user intent patterns
    - Track failed AI replies
    - Track SLA time
    - Decide what should go to Long-Term Memory
    - Fast detection of identity facts (name)
    """

    def __init__(
        self,
        max_history: int = 20,
        sla_seconds: int = 1800,
        user_id: str | None = None,
    ):
        self.max_history = max_history
        self.sla_seconds = sla_seconds
        self.user_id = user_id

        # =========================
        # Short-term conversation memory
        # =========================
        self._history: List[Dict[str, Any]] = []

        # =========================
        # Intent tracking
        # =========================
        self._intent_history = deque(maxlen=10)
        self._intent_counter = Counter()

        # =========================
        # Failed AI reply tracking
        # =========================
        self.failed_ai_replies = 0

        # =========================
        # SLA tracking
        # =========================
        self.conversation_start = datetime.utcnow()

    # ==================================================
    # PUBLIC API
    # ==================================================

    def add_user_message(self, content: str) -> str:
        """Add user message and detect intent"""
        self._add_message(role="user", content=content)

        intent = self._detect_intent(content)
        self._intent_history.append(intent)
        self._intent_counter[intent] += 1

        return intent

    def add_agent_message(self, content: str) -> None:
        """Add AI/agent message"""
        self._add_message(role="assistant", content=content)

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def get_formatted_history(self) -> str:
        return "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in self._history
        )

    def clear(self) -> None:
        self._history.clear()
        self._intent_history.clear()
        self._intent_counter.clear()
        self.failed_ai_replies = 0
        self.reset_sla()

    # ==================================================
    # INTENT TRACKING
    # ==================================================

    def get_intent_count(self, intent: str) -> int:
        return self._intent_counter.get(intent, 0)

    def get_recent_intents(self) -> List[str]:
        return list(self._intent_history)

    # ==================================================
    # FAILED AI REPLY TRACKING
    # ==================================================

    def mark_failed_ai_reply(self) -> None:
        self.failed_ai_replies += 1

    def reset_failed_ai_replies(self) -> None:
        self.failed_ai_replies = 0

    # ==================================================
    # SLA LOGIC
    # ==================================================

    def is_sla_breached(self) -> bool:
        elapsed = (datetime.utcnow() - self.conversation_start).total_seconds()
        return elapsed >= self.sla_seconds

    def reset_sla(self) -> None:
        self.conversation_start = datetime.utcnow()

    # ==================================================
    # LONG-TERM MEMORY DECISION
    # ==================================================

    def should_store_long_term(self, intent: str) -> bool:
        """
        Decide which intents are worth storing long-term
        """
        return intent in {
            "REFUND_DEMAND",
            "COMPLAINT",
            "HUMAN_REQUEST",
            "IDENTITY",
        }

    def extract_memory_text(self, message: str) -> str:
        return message.strip()

    # ==================================================
    # ⚡ IDENTITY FAST-PATH (STRONG 🔥)
    # ==================================================

    def extract_name(self, message: str) -> str | None:
        """
        Strong name extraction with false-positive protection.
        Supports English + Bangla.
        """

        msg = message.strip().lower()

        # ❌ Ignore common non-name words
        blacklist = {
            "fine", "okay", "angry", "sad", "happy",
            "ready", "tired", "having", "trouble", "problem"
        }

        patterns = [
            # English
            r"\bmy name is\s+([a-zA-Z]{2,}(?:\s[a-zA-Z]{2,})?)",
            r"\bi am\s+([a-zA-Z]{2,})",
            r"\bi'm\s+([a-zA-Z]{2,})",
            r"\bcall me\s+([a-zA-Z]{2,})",
            r"\bthis is\s+([a-zA-Z]{2,})",

            # Bangla
            r"আমার নাম\s+([অ-হA-Za-z]+)",
            r"আমি\s+([অ-হA-Za-z]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                name = match.group(1).strip().title()

                if name.lower() in blacklist:
                    return None

                return name

        return None

    def is_name_query(self, message: str) -> bool:
        """
        Detect questions asking about user's name.
        """
        msg = message.lower()
        return any(
            q in msg
            for q in [
                "what is my name",
                "do you remember my name",
                "who am i",
                "amar naam ki",
                "amar nam ki",
            ]
        )

    # ==================================================
    # INTERNAL HELPERS
    # ==================================================

    def _add_message(self, role: str, content: str) -> None:
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
        msg = message.lower()

        if self.extract_name(message):
            return "IDENTITY"

        if "refund" in msg:
            if any(x in msg for x in ["want", "now", "immediately"]):
                return "REFUND_DEMAND"
            return "REFUND_INFO"

        if any(x in msg for x in ["complaint", "angry", "not happy", "bad", "worst"]):
            return "COMPLAINT"

        if any(x in msg for x in ["human", "agent", "support"]):
            return "HUMAN_REQUEST"

        return "GENERAL"
