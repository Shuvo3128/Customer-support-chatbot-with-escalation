# 🤖 Customer Support AI Chatbot (RAG + Escalation)

An AI-powered **Customer Support Assistant** built with **Streamlit**, **LangChain**, **Ollama**, and **ChromaDB**.  
Supports **RAG-based answers**, **long-term memory**, **automatic escalation**, **admin dashboard**, and **human-in-the-loop support**.

---

## 🚀 Key Features

- 📚 PDF-based Knowledge Base (RAG)
- 🔍 Semantic Search with ChromaDB
- 🧠 Short & Long-Term Memory
- ⚡ Identity Handling (Name memory)
- 🎯 Intent Detection (Refund / Complaint / General)
- 🔁 Repeated Complaint Detection
- 🤖 Auto Escalation on AI Failure
- 🚨 Human Takeover Support
- 🧑‍💼 Admin Dashboard (Ticket Management)
- 🎫 Ticket Creation with Priority
- 📄 Source Transparency (PDF + Page)

---

## 🧰 Tech Stack

- **Frontend:** Streamlit  
- **LLM:** Ollama (LLaMA compatible models)  
- **Embeddings:** Ollama Embeddings  
- **Vector DB:** ChromaDB  
- **RAG Framework:** LangChain  
- **Backend:** Python  
- **Storage:** Local persistent DB (ChromaDB + JSON)

---

## 📁 Project Structure

```text
CUSTOMER_SUPPORT_CHATBOT/
│
├── app.py                    # Streamlit UI + Admin Dashboard
├── agent.py                  # Core AI agent (RAG + memory + escalation)
├── memory_manager.py         # Short & long-term memory + identity
├── admin_store.py            # Persistent admin ticket storage
├── admin_escalations.json    # Stored escalation tickets
├── vector_store.py           # ChromaDB + user memory store
├── document_processor.py     # PDF loading & chunking
├── tools.py                  # Ticketing & escalation tools
├── escalation_manager.py     # Escalation rules & severity logic
├── utils.py                  # UI helpers, logging, sessions
├── config.py                 # Central configuration
├── requirements.txt          # Dependencies
│
├── pdfFiles/                 # 📌 Place PDFs here for RAG
└── README.md

System Architecture – Customer Support AI Chatbot
🔹 High-Level Architecture Diagram
┌──────────────────────┐
│      End User        │
│  (Web / Browser)     │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│   Streamlit UI       │
│  (app.py)            │
│                      │
│ - Chat Interface     │
│ - Admin Dashboard    │
│ - PDF Loader         │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│        CustomerSupportAgent               │
│              (agent.py)                   │
│                                          │
│ ┌──────────────┐   ┌──────────────────┐ │
│ │ MemoryManager│   │ EscalationManager│ │
│ │ (Short + LT) │   │ (Rules & SLA)    │ │
│ └──────┬───────┘   └─────────┬────────┘ │
│        │                     │          │
│        ▼                     ▼          │
│ ┌────────────────────────────────────┐ │
│ │        Decision Engine              │ │
│ │  - Intent Detection                 │ │
│ │  - Identity Fast-Path (Name)        │ │
│ │  - Escalation Logic                 │ │
│ └──────────────┬─────────────────────┘ │
│                │                       │
│      ┌─────────▼─────────┐   ┌────────▼────────┐
│      │   RAG Pipeline     │   │ Human Takeover  │
│      │                   │   │ (Admin Mode)    │
│      └─────────┬─────────┘   └────────┬────────┘
│                │                       │
└────────────────┼───────────────────────┘
                 │
        ┌────────▼──────────┐
        │  Knowledge Base   │
        │  (ChromaDB)       │
        │  - PDF Embeddings │
        │  - Semantic Search│
        └────────┬──────────┘
                 │
        ┌────────▼──────────┐
        │   Ollama LLM      │
        │ (Answer Gen)     │
        └──────────────────┘

                 │
                 ▼
┌──────────────────────────────────────┐
│        Admin Store (Persistent)       │
│        admin_store.py                 │
│ - Tickets                             │
│ - Status                              │
│ - Conversation Snapshot               │
└──────────────────────────────────────┘
