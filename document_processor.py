"""
Document Processor
Responsible for loading, cleaning, and chunking documents
for the customer support knowledge base.
"""

import os
from typing import List
import logging

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

import config

logger = logging.getLogger(__name__)



class DocumentProcessor:
    def __init__(
        self,
        chunk_size: int = config.CHUNK_SIZE,
        chunk_overlap: int = config.CHUNK_OVERLAP,
    ):
        """
        Args:
            chunk_size: size of each text chunk
            chunk_overlap: overlap between chunks
        """

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

    # =========================
    # Public APIs
    # =========================

    def process_pdf(self, file_path: str) -> List[Document]:
        """Load and split a PDF file."""
        logger.info(f"Processing PDF: {file_path}")

        loader = PyPDFLoader(file_path)
        documents = loader.load()

        return self._split_documents(documents)

    def process_text_file(self, file_path: str) -> List[Document]:
        """Load and split a text file."""
        logger.info(f"Processing text file: {file_path}")

        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()

        return self._split_documents(documents)

    def process_folder(self, folder_path: str) -> List[Document]:
        """
        Process all supported files inside a folder.
        Supported: PDF, TXT
        """
        all_docs: List[Document] = []

        if not os.path.exists(folder_path):
            logger.warning(f"Folder not found: {folder_path}")
            return all_docs

        for filename in os.listdir(folder_path):
            full_path = os.path.join(folder_path, filename)

            if filename.lower().endswith(".pdf"):
                all_docs.extend(self.process_pdf(full_path))

            elif filename.lower().endswith(".txt"):
                all_docs.extend(self.process_text_file(full_path))

            else:
                logger.warning(f"Skipping unsupported file: {filename}")

        logger.info(f"Total processed chunks: {len(all_docs)}")
        return all_docs

    # =========================
    # Internal Helpers
    # =========================

    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into clean chunks."""
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split into {len(chunks)} chunks")
        return chunks
