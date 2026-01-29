"""
Customer Support AI Assistant - Streamlit App
--------------------------------------------

Features:
- AI-powered customer support
- Long-term user memory
- Intent detection
- Auto escalation
- Ticketing with priority
- RAG with Source Documents
- 🧑‍💼 Admin Dashboard (2-way Human Chat)
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
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()

    if "agent" not in st.session_state:
        st.session_state.agent = CustomerSupportAgent(
            user_id=st.session_state.session_id
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "escalated" not in st.session_state:
        st.session_state.escalated = False


# --------------------------------------------------
# UI HELPERS
# --------------------------------------------------

def sync_admin_replies():
    """
    STEP 2.4 + 2.5
    Pull admin replies from AdminStore and sync to user chat
    (works across refresh)
    """
    agent = st.session_state.agent
    admin_store = agent.admin_store

    escalations = admin_store.list_escalations()

    for esc in escalations:
        if esc["user_id"] != st.session_state.session_id:
            continue

        for msg in esc["conversation"]:
            if msg["role"] == "admin":
                already_added = any(
                    m["role"] == "admin"
                    and m["content"] == msg["content"]
                    for m in st.session_state.messages
                )
                if not already_added:
                    st.session_state.messages.append(
                        {
                            "role": "admin",
                            "content": msg["content"],
                        }
                    )


def display_chat_history():
    for msg in st.session_state.messages:
        role = msg["role"]

        if role == "admin":
            with st.chat_message("assistant"):
                st.markdown(f"🧑‍💼 **Support Agent:** {msg['content']}")
        else:
            with st.chat_message(role):
                st.markdown(msg["content"])


# --------------------------------------------------
# MAIN APP
# --------------------------------------------------

def main():
    init_session_state()

    # 🔄 STEP 2.4 + 2.5: Sync admin replies every run
    sync_admin_replies()

    st.title("🤖 Customer Support AI Assistant")
    st.caption(
        "AI support with long-term memory, escalation & human-in-the-loop dashboard"
    )

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
        # ADMIN MODE
        # =========================
        st.subheader("🧑‍💼 Admin Mode")
        admin_mode = st.checkbox("Enable Admin Dashboard")

        st.divider()

        # =========================
        # KNOWLEDGE BASE LOADER
        # =========================
        st.subheader("📄 Knowledge Base")

        if st.button("📥 Load PDFs"):
            from document_processor import DocumentProcessor

            processor = DocumentProcessor()
            chunks = processor.process_folder(config.PDF_DIR)
            st.session_state.agent.vector_store_manager.create_store(chunks)

            st.success("Knowledge base loaded successfully!")

    # ==================================================
    # ADMIN DASHBOARD UI
    # ==================================================
    if admin_mode:
        st.header("🚨 Admin Dashboard – Escalated Tickets")

        admin_store = st.session_state.agent.admin_store
        escalations = admin_store.list_escalations()

        if not escalations:
            st.info("No escalated tickets yet.")
        else:
            for esc in escalations:
                with st.expander(
                    f"🎫 {esc['ticket_id']} | {esc['priority']} | {esc['status']}"
                ):
                    st.markdown(f"**User ID:** `{esc['user_id']}`")
                    st.markdown(f"**Reason:** {esc['reason']}")
                    st.markdown(f"**Created:** {esc['created_at']}")

                    # --------------------------
                    # STATUS UPDATE
                    # --------------------------
                    new_status = st.selectbox(
                        "Update Ticket Status",
                        ["OPEN", "IN_PROGRESS", "RESOLVED"],
                        index=["OPEN", "IN_PROGRESS", "RESOLVED"].index(
                            esc["status"]
                        ),
                        key=f"status_{esc['ticket_id']}",
                    )

                    if st.button(
                        "💾 Save Status",
                        key=f"save_{esc['ticket_id']}",
                    ):
                        admin_store.update_status(
                            esc["ticket_id"], new_status
                        )
                        st.success("Status updated")
                        st.rerun()

                    # --------------------------
                    # CONVERSATION VIEW
                    # --------------------------
                    st.markdown("### 🗨️ Conversation History")
                    for msg in esc["conversation"]:
                        st.markdown(
                            f"**{msg['role'].upper()}:** {msg['content']}"
                        )

                    # --------------------------
                    # ADMIN REPLY
                    # --------------------------
                    st.markdown("### ✍️ Admin Reply")

                    admin_reply = st.text_area(
                        "Write reply to user",
                        key=f"reply_{esc['ticket_id']}",
                    )

                    if st.button(
                        "📨 Send Reply",
                        key=f"send_{esc['ticket_id']}",
                    ):
                        admin_store.add_admin_reply(
                            esc["ticket_id"], admin_reply
                        )

                        st.success("Reply sent to user")
                        st.rerun()

        st.divider()

    # ==================================================
    # CHAT UI (USER SIDE)
    # ==================================================
    display_chat_history()

    if prompt := st.chat_input("Type your message here..."):
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
