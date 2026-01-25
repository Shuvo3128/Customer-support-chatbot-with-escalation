"""
Utility functions for Customer Support AI Assistant
Shared helpers used across app, agent, tools, memory, and escalation
"""

import time
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any
import streamlit as st

logger = logging.getLogger(__name__)

# ==========================================================
# LOGGING
# ==========================================================

def setup_logging(level=logging.INFO):
    """Setup global logging format."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info("Logging configured successfully")


# ==========================================================
# STREAMLIT UI HELPERS
# ==========================================================

def typing_effect(text: str, delay: float = 0.01):
    """
    Display text with typing animation (chat-like effect).
    """
    placeholder = st.empty()
    rendered_text = ""
    for char in text:
        rendered_text += char
        placeholder.markdown(rendered_text)
        time.sleep(delay)


def show_status(message: str, success: bool = True):
    """
    Display success or error message.
    """
    if success:
        st.success(message)
    else:
        st.error(message)


# ==========================================================
# CHAT HISTORY HELPERS
# ==========================================================

def format_chat_history(messages: List[Dict[str, str]]) -> str:
    """
    Convert chat history into readable text.
    """
    output = []
    for msg in messages:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        output.append(f"{role}: {content}")
    return "\n\n".join(output)


def generate_session_id() -> str:
    """Generate unique session ID."""
    return str(uuid.uuid4())


# ==========================================================
# FILE & DOCUMENT HELPERS
# ==========================================================

def validate_pdf(file) -> bool:
    """Check if uploaded file is a valid PDF."""
    if not file:
        return False
    return file.name.lower().endswith(".pdf")


def file_size_mb(file) -> float:
    """Return file size in MB."""
    return round(file.size / (1024 * 1024), 2)


# ==========================================================
# RAG SOURCE FORMATTING
# ==========================================================

def format_sources(docs: List[Any]) -> str:
    """
    Format RAG source documents for UI display.
    """
    if not docs:
        return "No sources available."

    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "N/A")
        formatted.append(
            f"**{i}. Source:** {source} (Page {page})"
        )

    return "\n".join(formatted)


# ==========================================================
# TIME & TOKEN UTILITIES
# ==========================================================

def current_timestamp() -> str:
    """Return formatted current timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def estimate_tokens(text: str) -> int:
    """
    Rough token estimation.
    1 token ≈ 4 characters
    """
    return max(1, len(text) // 4)


def truncate_text(text: str, max_length: int = 500) -> str:
    """Trim long text safely."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


# ==========================================================
# ESCALATION HELPERS
# ==========================================================

def create_ticket_payload(
    user_message: str,
    reason: str,
    session_id: str,
) -> Dict[str, Any]:
    """
    Create structured payload for human escalation.
    """
    return {
        "ticket_id": f"TICKET-{uuid.uuid4().hex[:8]}",
        "created_at": current_timestamp(),
        "session_id": session_id,
        "user_message": user_message,
        "escalation_reason": reason,
        "status": "OPEN",
    }
