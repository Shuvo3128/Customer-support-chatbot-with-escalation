"""
Escalation Manager
Determines escalation LEVEL for customer queries.
"""

import re
from typing import Dict


class EscalationManager:
    def __init__(self):
        # 🔴 HIGH → Immediate human escalation
        self.high_patterns = [
            r"\btalk to human\b",
            r"\breal agent\b",
            r"\bhuman agent\b",
            r"\bi want a refund\b",
            r"\brefund denied\b",
            r"\bcomplaint\b",
            r"\bnot happy\b",
            r"\bangry\b",
            r"\blegal\b",
            r"\bscam\b",
            r"\bfraud\b",
            r"\bhacked\b",
            r"\bbad service\b",
            r"\bworst experience\b",
        ]

        # 🟠 MEDIUM → Explain first, then human if needed
        self.medium_patterns = [
            r"\bhow can i get a refund\b",
            r"\brefund process\b",
            r"\brefund procedure\b",
            r"\brefund steps\b",
            r"\bpayment issue\b",
            r"\bbilling issue\b",
        ]

        # 🟢 LOW → Informational (never escalate)
        self.low_patterns = [
            r"\brefund policy\b",
            r"\brefund rules\b",
            r"\brefund terms\b",
            r"\babout refunds\b",
            r"\bwhat does.*refund\b",
            r"\bhow does.*refund\b",
            r"\bwhat is this document about\b",
            r"\bsummarize\b",
        ]

    def should_escalate(self, user_message: str) -> Dict[str, str]:
        """
        Decide escalation level.

        Returns:
        {
            "level": "LOW" | "MEDIUM" | "HIGH",
            "reason": str
        }
        """
        message = user_message.lower()

        # 🔴 HIGH escalation
        for pattern in self.high_patterns:
            if re.search(pattern, message):
                return {
                    "level": "HIGH",
                    "reason": "User complaint, demand, or sensitive issue detected"
                }

        # 🟠 MEDIUM escalation
        for pattern in self.medium_patterns:
            if re.search(pattern, message):
                return {
                    "level": "MEDIUM",
                    "reason": "Sensitive topic – explain policy first"
                }

        # 🟢 LOW escalation
        for pattern in self.low_patterns:
            if re.search(pattern, message):
                return {
                    "level": "LOW",
                    "reason": "Informational query"
                }

        # 🟢 Default
        return {
            "level": "LOW",
            "reason": "General query"
        }
