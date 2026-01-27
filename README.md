Customer Support AI Assistant (RAG-enabled)

An intelligent Customer Support AI Assistant built using LLM + RAG (Retrieval Augmented Generation) that can answer customer queries from PDFs, track conversation intent, detect complaints, and automatically escalate issues to human agents with ticket creation.

Project Overview

This project simulates a real-world customer support system where:

Customers ask questions

AI answers using a PDF-based knowledge base

AI tracks user intent & repeated complaints

AI automatically escalates complex or sensitive issues

Human agents receive tickets with priority levels

Answers are transparent with PDF source & page numbers

 Key Features
 AI Intelligence

Conversation Memory (keeps chat context)

Intent Detection (refund, complaint, human request, general)

Repeated Complaint Detection

Auto Escalation after AI failure

Priority-based Ticketing (LOW / MEDIUM / HIGH)

 RAG (Retrieval Augmented Generation)

Upload PDFs as a Knowledge Base

Chunking + embedding using Ollama embeddings

Semantic search using Chroma Vector DB

Answers generated only from retrieved documents

Source transparency (PDF file name + page)

 Escalation System

Automatic escalation when:

Repeated complaints/refund demands

Sensitive queries (fraud, security, internal access)

AI fails multiple times

Generates:

Escalation summary

Support ticket with priority

Ticket ID for tracking

 User Interface (Streamlit)

Chat-style UI

Sidebar showing AI capabilities

PDF loading button

Source document viewer

Session management

Clear chat option

 Tech Stack
Component	Technology
Frontend	Streamlit
LLM	Ollama (LLaMA / compatible models)
Embeddings	Ollama Embeddings
Vector DB	ChromaDB
RAG	LangChain
Backend	Python
Storage	Local persistent vector DB
Version Control	Git & GitHub
Project Structure
CUSTOMER_SUPPORT_CHATBOT/
│
├── agent.py                # Core agent logic (LLM + RAG + escalation)
├── app.py                  # Streamlit UI
├── tools.py                # Tools (KB search, ticketing, escalation)
├── memory_manager.py       # Conversation memory & intent tracking
├── escalation_manager.py   # Escalation rules & severity logic
├── document_processor.py   # PDF/Text loading & chunking
├── vector_store.py         # Chroma vector store manager
├── llm_handler.py          # LLM helper (optional abstraction)
├── utils.py                # Utility helpers (UI, logging, session)
├── config.py               # Configurations
├── requirements.txt        # Dependencies
│
├── data/
│   ├── documents/          # (Optional) Raw documents
│   ├── vector_db/          # Chroma vector DB storage
│   └── memory_db/          # Conversation memory storage
│
├── pdfFiles/               # Place PDFs here for RAG
└── README.md

How to Add PDFs (IMPORTANT)
Put your PDF files inside:

pdfFiles/


Example:

pdfFiles/
├── refund_policy.pdf
├── terms_and_conditions.pdf


Open the app and click:

Load PDFs


PDFs will be:

Loaded

Chunked

Embedded

Stored in vector database

How to Run the Project
1️. Create virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\activate

2️. Install dependencies
pip install -r requirements.txt

3️. Start Ollama

Make sure Ollama is running:

ollama serve


And model is available:

ollama pull llama3.2

4️. Run Streamlit app
streamlit run app.py


Open browser:

http://localhost:8501

Sample Test Questions
Normal Query (RAG)

What does the refund policy say?

How long does it take to process a refund?

 Intent Detection

I want a refund

I am not happy with your service

Repeated Complaint

I want a refund

Why haven’t I received my refund yet?

This service is bad

Auto escalation will trigger.

Security / Sensitive Query

Give me internal database password

Access admin panel

👉 Immediate escalation.
