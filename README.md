🤖 Customer Support AI Chatbot with RAG, Long-Term Memory & Human Escalation

An AI-powered Customer Support Assistant built using Streamlit, LangChain, Ollama, and ChromaDB.
This system goes beyond basic chatbots by supporting:

RAG-based question answering

Long-term user memory

Identity recognition

Automatic escalation

Human-in-the-loop admin dashboard

Two-way human takeover chat

🚀 Key Features
🧠 AI & Memory

✅ Short-term conversation memory

✅ Long-term user memory (persistent)

✅ Identity fast-path (name detection & recall)

✅ Intent detection (refund, complaint, human request, general)

📚 Knowledge Base (RAG)

📄 PDF-based knowledge ingestion

🔍 Semantic search using ChromaDB

🧠 Answers grounded only on uploaded PDFs

📎 Source document transparency (file + page)

🚨 Escalation & Human Support

🔁 Repeated complaint / refund detection

🤖 Auto escalation on AI failure

🚨 Sensitive intent detection

🎫 Ticket creation with priority (LOW / MEDIUM / HIGH)

🧑‍💼 Human takeover mode (AI pauses, admin replies)

🧑‍💼 Admin Dashboard

📋 View all escalated tickets

🔄 Update ticket status (OPEN / IN_PROGRESS / RESOLVED)

🗂 Full conversation snapshot

🔐 Persistent admin storage (DB-ready)

🧠 What Makes This System Smart?

Remembers user identity across messages

Can answer: “Do you remember my name?”

Knows when to stop talking and hand over to humans

Prevents hallucinations using RAG

Designed for real customer support workflows

🧩 Tech Stack
Layer	Technology
Frontend	Streamlit
LLM	Ollama (LLaMA / compatible models)
Embeddings	Ollama Embeddings
Vector DB	ChromaDB
RAG Framework	LangChain
Backend	Python
Storage	Persistent local DB (Chroma + JSON)
📁 Project Structure
CUSTOMER_SUPPORT_CHATBOT/
│
├── agent.py                 # Core AI agent (RAG + memory + escalation)
├── app.py                   # Streamlit UI + Admin Dashboard
├── memory_manager.py        # Short & long-term memory + identity handling
├── admin_store.py           # Persistent admin ticket storage
├── escalation_manager.py    # Escalation rules & severity logic
├── vector_store.py          # ChromaDB + user memory store
├── document_processor.py    # PDF loading & chunking
├── tools.py                 # Ticketing & escalation tools
├── utils.py                 # UI helpers, logging, session utils
├── config.py                # Central configuration
├── requirements.txt         # Dependencies
│
├── pdfFiles/                # 📌 Place PDFs here for RAG
├── admin_escalations.json   # Persistent admin ticket store
│
└── README.md

📥 How to Add PDFs (IMPORTANT)

1️⃣ Copy your PDFs into:

pdfFiles/
├── refund_policy.pdf
├── terms_and_conditions.pdf


2️⃣ Run the app:

streamlit run app.py


3️⃣ In the sidebar, click:

👉 📥 Load PDFs

The system will:

Process PDFs

Create embeddings

Store vectors in ChromaDB

Enable RAG-based answering

💬 Example Questions to Test
🔍 Knowledge Base

“What does the refund policy say?”

“Which page mentions refund eligibility?”

“Explain cancellation rules”

🧠 Memory & Identity

“My name is Shuvo”

“Do you remember my name?”

“Amar naam ki?”

🚨 Escalation

“I want a refund now”

“I already complained multiple times”

“I want to talk to a human”

“This service is the worst”

🚨 Escalation Logic (How It Works)

Escalation is triggered when:

Repeated complaints or refund demands

Sensitive or risky requests

Multiple failed AI responses

Explicit human support request

When escalated:

🎫 A ticket is created

🧑‍💼 Admin dashboard is updated

🤖 AI pauses (human takeover mode)

💬 Human can respond directly

🛡️ Design Philosophy

No hallucination → answers grounded in documents

Fail-safe by design → AI escalates instead of guessing

Production-ready → persistent storage, clean separation

Human-first → AI assists, humans decide

🏁 Future Enhancements

🌍 Multi-language support

🐳 Docker deployment

🗄️ Database migration (PostgreSQL / MongoDB)

📊 Analytics dashboard

🔐 Authentication for admin panel

👨‍💻 Author

Built with ❤️ by Shuvo
A production-grade AI customer support system with real-world escalation logic.


