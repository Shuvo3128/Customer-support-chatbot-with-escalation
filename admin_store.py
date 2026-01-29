"""
Admin Store (Production-Ready)
------------------------------
Responsibilities:
- Persist escalated tickets
- Track ticket status & priority
- Store full conversation snapshot
- Store admin (human) replies
- Safe for Streamlit re-runs
- Easy migration to DB later
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from threading import Lock


class AdminStore:
    """
    Central storage for escalated tickets
    """

    STORAGE_FILE = "admin_escalations.json"

    def __init__(self):
        self._lock = Lock()
        self._escalations: List[Dict] = []
        self._load_from_disk()

    # ==================================================
    # PERSISTENCE
    # ==================================================

    def _load_from_disk(self) -> None:
        """Load escalations from disk if exists."""
        if not os.path.exists(self.STORAGE_FILE):
            self._escalations = []
            return

        try:
            with open(self.STORAGE_FILE, "r", encoding="utf-8") as f:
                self._escalations = json.load(f)
        except Exception:
            # Corrupted file safety
            self._escalations = []

    def _save_to_disk(self) -> None:
        """Persist escalations to disk."""
        with open(self.STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(self._escalations, f, indent=2)

    # ==================================================
    # CORE API
    # ==================================================

    def add_escalation(
        self,
        ticket_id: str,
        user_id: str,
        reason: str,
        priority: str,
        conversation: List[Dict],
    ) -> None:
        """
        Store a new escalation entry
        """
        escalation = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "reason": reason,
            "priority": priority,
            "status": "OPEN",
            "conversation": conversation,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        with self._lock:
            self._escalations.append(escalation)
            self._save_to_disk()

    def list_escalations(self) -> List[Dict]:
        """
        Return all escalated tickets (latest first)
        """
        with self._lock:
            return sorted(
                self._escalations,
                key=lambda x: x["created_at"],
                reverse=True,
            )

    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """
        Fetch a single ticket by ID
        """
        with self._lock:
            for esc in self._escalations:
                if esc["ticket_id"] == ticket_id:
                    return esc
        return None

    # ==================================================
    # STATUS MANAGEMENT
    # ==================================================

    def update_status(self, ticket_id: str, status: str) -> bool:
        """
        Update ticket status
        Allowed: OPEN | IN_PROGRESS | RESOLVED
        """
        status = status.upper()

        if status not in {"OPEN", "IN_PROGRESS", "RESOLVED"}:
            return False

        with self._lock:
            for esc in self._escalations:
                if esc["ticket_id"] == ticket_id:
                    esc["status"] = status
                    esc["updated_at"] = datetime.utcnow().isoformat()
                    self._save_to_disk()
                    return True

        return False

    # ==================================================
    # 🧑‍💼 ADMIN → USER REPLY (STEP 2.1 ✅)
    # ==================================================

    def add_admin_reply(self, ticket_id: str, message: str) -> bool:
        """
        Add admin (human) reply to ticket conversation
        """
        with self._lock:
            for esc in self._escalations:
                if esc["ticket_id"] == ticket_id:
                    esc["conversation"].append(
                        {
                            "role": "admin",
                            "content": message,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                    esc["updated_at"] = datetime.utcnow().isoformat()
                    self._save_to_disk()
                    return True
        return False

    # ==================================================
    # ANALYTICS (BASIC)
    # ==================================================

    def count_by_status(self) -> Dict[str, int]:
        """
        Return count of tickets by status
        """
        counts = {"OPEN": 0, "IN_PROGRESS": 0, "RESOLVED": 0}

        with self._lock:
            for esc in self._escalations:
                counts[esc["status"]] += 1

        return counts

    def count_by_priority(self) -> Dict[str, int]:
        """
        Return count of tickets by priority
        """
        counts = {}

        with self._lock:
            for esc in self._escalations:
                pr = esc["priority"]
                counts[pr] = counts.get(pr, 0) + 1

        return counts
