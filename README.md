# 🤖 Customer Support AI Chatbot with RAG & Escalation

An AI-powered **Customer Support Assistant** built using **Streamlit**, **LangChain**, **Ollama**, and **ChromaDB**.  
The system supports **RAG-based question answering**, **intent detection**, **automatic escalation**, and **human ticketing** with full **source transparency**.

---

## 🚀 Key Features

- 📚 **PDF Knowledge Base (RAG)**
- 🔍 **Semantic Search using ChromaDB**
- 🧠 **Conversation Memory**
- 🎯 **Intent Detection (Refund / Complaint / General)**
- 🔁 **Repeated Complaint Detection**
- 🤖 **Auto Escalation on AI Failure**
- 🚨 **Human Escalation System**
- 🎫 **Ticket Creation with Priority**
- 📄 **RAG Source Transparency (PDF + Page)**
- 🧹 **Clear Chat & Session Management**

---

## 🧠 AI Capabilities

- Answers user questions using **only uploaded PDFs**
- Shows **exact source documents** used to answer
- Detects **sensitive / repeated issues**
- Automatically escalates to human support
- Generates **support tickets** with priority levels

---

## 🧩 Tech Stack

| Layer | Technology |
|-----|-----------|
| Frontend | Streamlit |
| LLM | Ollama (LLaMA / compatible models) |
| Embeddings | Ollama Embeddings |
| Vector DB | ChromaDB |
| RAG Framework | LangChain |
| Backend | Python |
| Storage | Local persistent vector DB |

---

## 📁 Project Structure

```text
CUSTOMER_SUPPORT_CHATBOT/
│
├── agent.py                 # Core AI agent logic (LLM + RAG + Escalation)
├── app.py                   # Streamlit UI
├── tools.py                 # Tools (KB search, ticketing, escalation)
├── memory_manager.py        # Conversation memory & intent tracking
├── escalation_manager.py    # Escalation rules & severity logic
├── document_processor.py    # PDF/Text loading & chunking
├── vector_store.py          # Chroma vector DB manager
├── llm_handler.py           # (Optional) LLM abstraction
├── utils.py                 # Utility helpers (UI, logging, session)
├── config.py                # Configurations
├── requirements.txt         # Dependencies
│
├── data/
│   ├── documents/           # (Optional) Raw documents
│   ├── vector_db/           # Chroma vector DB storage
│   └── memory_db/           # Conversation memory storage
│
├── pdfFiles/                # 📌 Place PDFs here for RAG
│
└── README.md
