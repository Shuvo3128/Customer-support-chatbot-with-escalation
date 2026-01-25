"""
Global Configuration File
Customer Support Chatbot with Agent + RAG + Escalation
"""

import os
from pathlib import Path

# ==========================================================
# BASE PATHS
# ==========================================================

BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "documents"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
MEMORY_DB_DIR = DATA_DIR / "memory_db"

# Create directories if not exist
for directory in [DATA_DIR, PDF_DIR, VECTOR_DB_DIR, MEMORY_DB_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# ==========================================================
# LLM CONFIGURATION
# ==========================================================

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_EMBEDDING_MODEL = os.getenv(
    "OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"
)

# Azure OpenAI (optional – enterprise ready)
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT", "gpt-4"
)
AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
)

# Common LLM parameters
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))


# ==========================================================
# DOCUMENT PROCESSING (RAG)
# ==========================================================

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

VECTOR_COLLECTION_NAME = "customer_support_docs"


# ==========================================================
# MEMORY CONFIGURATION
# ==========================================================

# buffer | buffer_window | summary | vector | combined
DEFAULT_MEMORY_TYPE = os.getenv("MEMORY_TYPE", "buffer")

MEMORY_K = int(os.getenv("MEMORY_K", "6"))  # window size
MEMORY_MAX_TOKENS = int(os.getenv("MEMORY_MAX_TOKENS", "2000"))

VECTOR_MEMORY_COLLECTION = "conversation_memory"


# ==========================================================
# TOOLS CONFIGURATION
# ==========================================================

TOOLS_ENABLED = {
    "calculator": True,
    "datetime": True,
    "python_repl": True,
    "web_search": True,
    "rag_search": True,
    "ticket_creator": True,
}

WEB_SEARCH_MAX_RESULTS = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))
PYTHON_REPL_TIMEOUT = int(os.getenv("PYTHON_REPL_TIMEOUT", "20"))


# ==========================================================
# ESCALATION CONFIGURATION
# ==========================================================

ESCALATION_ENABLED = True

ESCALATION_CONFIDENCE_THRESHOLD = 0.35

ESCALATION_KEYWORDS = {
    "human_request": [
        "talk to human", "real agent", "customer support"
    ],
    "sensitive": [
        "payment", "refund", "billing", "fraud", "scam", "legal"
    ],
    "anger": [
        "angry", "worst", "terrible", "complaint", "not happy"
    ],
}


# ==========================================================
# STREAMLIT UI CONFIGURATION
# ==========================================================

APP_TITLE = "Customer Support AI Assistant"
APP_ICON = "🎧"
APP_LAYOUT = "wide"

WELCOME_MESSAGE = (
    "👋 Hi! I'm your AI customer support assistant.\n\n"
    "I can help you with questions, documents, and support tickets."
)

HUMAN_ESCALATION_MESSAGE = (
    "⚠️ This issue has been escalated to a human support agent.\n"
    "A support ticket has been created."
)


# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# =========================
# Vector Store Configuration
# =========================

COLLECTION_NAME = "customer_support_kb"
CHROMA_PERSIST_DIR = "vectorDB"

