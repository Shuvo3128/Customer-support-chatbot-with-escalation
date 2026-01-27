"""
Customer Support AI Assistant - Streamlit App
--------------------------------------------

Features:
- AI-powered customer support
- Conversation memory
- Intent detection
- Auto escalation
- Ticketing with priority
- RAG with Source Documents (Teacher Killer 🔥)
"""

import streamlit as st
import logging

from agent import CustomerSupportAgent
from utils import (
    setup_logging,
    typing_effect,
    generate_session_id,
)

import config

# --------------------------------------------------
# SETUP
# --------------------------------------------------

setup_logging()
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Customer Support AI",
    page_icon="🤖",
    layout="wide",
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

def init_session_state():
    if "agent" not in st.session_state:
        st.session_state.agent = CustomerSupportAgent()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()

    if "escalated" not in st.session_state:
        st.session_state.escalated = False


# --------------------------------------------------
# UI HELPERS
# --------------------------------------------------

def display_chat_history():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


# --------------------------------------------------
# MAIN APP
# --------------------------------------------------

def main():
    init_session_state()

    # Header
    st.title("🤖 Customer Support AI Assistant")
    st.caption("AI support with memory, intent detection & automatic escalation")

    # ==================================================
    # SIDEBAR
    # ==================================================
    with st.sidebar:
        st.header("⚙️ Controls")

        if st.button("🧹 Clear Chat"):
            st.session_state.messages = []
            st.session_state.agent.clear_memory()
            st.session_state.escalated = False
            st.success("Chat cleared")
            st.rerun()

        st.divider()

        st.subheader("🧾 Session Info")
        st.write(f"**Session ID:** `{st.session_state.session_id}`")

        if st.session_state.escalated:
            st.error("🚨 Conversation escalated to human support")

        st.divider()

        # =========================
        # 🧠 AI CAPABILITIES PANEL
        # =========================
        st.subheader("🧠 AI Capabilities")

        capabilities = [
            "📚 Knowledge Base (PDF Search)",
            "🧠 Conversation Memory",
            "🎯 Intent Detection",
            "🔁 Repeated Complaint Detection",
            "🤖 Auto Escalation (AI Failure)",
            "🚨 Human Escalation System",
            "🎫 Ticket Creation with Priority",
            "📄 RAG Source Transparency (PDF + Page)",
        ]

        for cap in capabilities:
            st.success(cap)

        st.divider()

        # =========================
        # KNOWLEDGE BASE LOADER (FIXED 🔥)
        # =========================
        st.subheader("📄 Knowledge Base")

        if st.button("📥 Load PDFs"):
            from document_processor import DocumentProcessor

            processor = DocumentProcessor()
            chunks = processor.process_folder(config.PDF_DIR)

            # 🔥 IMPORTANT FIX: use agent's vector store
            st.session_state.agent.vector_store_manager.create_store(chunks)

            st.success("Knowledge base loaded successfully!")

    # ==================================================
    # CHAT UI
    # ==================================================

    display_chat_history()

    if prompt := st.chat_input("Type your message here..."):
        # Save user message
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.agent.get_full_response(prompt)

                answer = result.get("output", "Sorry, I couldn't respond.")
                typing_effect(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

                if result.get("escalated"):
                    st.session_state.escalated = True

                # ==================================================
                # 🔥 SHOW RAG SOURCE DOCUMENTS
                # ==================================================
                documents = result.get("source_documents", [])

                if documents:
                    with st.expander("📚 Source Documents"):
                        for doc in documents:
                            st.markdown(
                                f"""
**File:** {doc.metadata.get('source', 'Unknown')}
**Page:** {doc.metadata.get('page', 'N/A')}

{doc.page_content[:500]}...
"""
                            )


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":
    main()
