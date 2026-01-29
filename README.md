🤖 Customer Support AI Chatbot

RAG • Long-Term Memory • Escalation • Admin Dashboard

An AI-powered Customer Support Assistant built with Streamlit, LangChain, Ollama, and ChromaDB.
Designed for real-world customer support workflows with hallucination-free answers, automatic escalation, and human-in-the-loop control.

✨ Key Features

📚 RAG-based PDF Knowledge Base

🔍 Semantic Search with ChromaDB

🧠 Short-term + Long-term Memory

⚡ Identity Fast-Path (Name Detection & Recall)

🎯 Intent Detection (Refund / Complaint / General)

🔁 Repeated Complaint Detection

🤖 Auto Escalation on AI Failure

🧑‍💼 Human Takeover (2-way chat)

🎫 Admin Dashboard with Ticket Management

📄 Source Transparency (PDF + Page)

🧠 How It Works

User asks a question

Relevant PDFs are retrieved using RAG

AI answers using only retrieved context

Memory tracks intent & user identity

Repeated / sensitive issues → Escalation

Admin reviews & takes over if needed

🧰 Tech Stack

Frontend: Streamlit

LLM: Ollama (LLaMA compatible models)

Embeddings: Ollama Embeddings

Vector DB: ChromaDB

RAG: LangChain

Backend: Python

Storage: Local persistent DB (Chroma + JSON)
