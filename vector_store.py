"""
Vector Store Manager
Handles knowledge base storage and semantic search (Windows-safe)
+ Long-Term User Memory Store
"""

import os
import logging
from typing import List, Optional

import chromadb
from chromadb.config import Settings

from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

import config

logger = logging.getLogger(__name__)


# ==================================================
# MAIN VECTOR STORE (KNOWLEDGE BASE - RAG)
# ==================================================

class VectorStoreManager:
    def __init__(
        self,
        collection_name: str = config.COLLECTION_NAME,
        persist_dir: str = config.CHROMA_PERSIST_DIR,
        embedding_model: Optional[str] = None,
    ):
        """
        Args:
            collection_name: Name of Chroma collection
            persist_dir: Directory for vector DB
            embedding_model: Ollama embedding model name
        """

        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.embedding_model = embedding_model or config.OLLAMA_EMBEDDING_MODEL

        # Ensure directory exists (Windows-safe)
        os.makedirs(self.persist_dir, exist_ok=True)

        # Ollama embeddings
        self.embeddings = OllamaEmbeddings(
            model=self.embedding_model,
            base_url=config.OLLAMA_BASE_URL,
        )

        # Chroma persistent client
        self.client = chromadb.Client(
            Settings(
                persist_directory=self.persist_dir,
                anonymized_telemetry=False,
            )
        )

        self._vector_store: Optional[Chroma] = None

        logger.info("VectorStoreManager initialized")

    # ==================================================
    # VECTOR STORE LIFECYCLE
    # ==================================================

    def create_store(self, documents: List[Document]) -> None:
        """
        Create vector store from documents.
        """

        if not documents:
            logger.warning("No documents provided to create vector store")
            return

        self._vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_dir,
        )

        logger.info(f"Vector store created with {len(documents)} documents")

    def load_store(self) -> Optional[Chroma]:
        """Load existing vector store from disk."""

        if not os.path.exists(self.persist_dir):
            logger.warning("Vector store directory not found")
            return None

        try:
            self._vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_dir,
            )
            logger.info("Vector store loaded from disk")
            return self._vector_store
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            return None

    def get_vector_store(self) -> Optional[Chroma]:
        """
        Used by agent.py & tools.py
        """
        if self._vector_store is None:
            return self.load_store()
        return self._vector_store

    def clear_store(self) -> None:
        """
        Clears in-memory reference only.
        Does NOT delete files (Windows-safe)
        """
        self._vector_store = None
        logger.info("Vector store reference cleared")

    # ==================================================
    # 🔍 SEARCH (RAG CORE)
    # ==================================================

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Perform semantic similarity search.
        """

        if self._vector_store is None:
            self.load_store()

        if self._vector_store is None:
            logger.warning("Vector store not initialized")
            return []

        return self._vector_store.similarity_search(query, k=k)


# ==================================================
# 🔐 LONG-TERM USER MEMORY STORE (NEW 🔥)
# ==================================================

class UserMemoryStore:
    """
    Persistent Long-Term Memory per user using Vector DB
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.collection_name = f"user_memory_{user_id}"

        # Ensure directory exists
        os.makedirs(config.CHROMA_PERSIST_DIR, exist_ok=True)

        self.embeddings = OllamaEmbeddings(
            model=config.OLLAMA_EMBEDDING_MODEL,
            base_url=config.OLLAMA_BASE_URL,
        )

        self.store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=config.CHROMA_PERSIST_DIR,
        )

        logger.info(f"UserMemoryStore initialized for user: {user_id}")

    def add_memory(self, text: str, metadata: dict):
        """
        Store a memory entry for the user
        """
        self.store.add_texts(
            texts=[text],
            metadatas=[metadata],
        )

    def get_relevant_memory(self, query: str, k: int = 3) -> List[Document]:
        """
        Retrieve relevant past memories for the user
        """
        return self.store.similarity_search(query, k=k)
