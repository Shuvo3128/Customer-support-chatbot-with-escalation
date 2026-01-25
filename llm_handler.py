"""
LLM Handler
Centralized, lightweight interface for Ollama LLM usage
"""

import logging
from langchain_ollama import ChatOllama
import config

logger = logging.getLogger(__name__)


class LLMHandler:
    """
    Handles all LLM interactions.
    No memory, no retrieval logic here.
    """

    def __init__(
        self,
        model: str = config.OLLAMA_MODEL,
        base_url: str = config.OLLAMA_BASE_URL,
        temperature: float = config.LLM_TEMPERATURE,
    ):
        self.model = model
        self.base_url = base_url
        self.temperature = temperature

        self._llm = ChatOllama(
            model=self.model,
            base_url=self.base_url,
            temperature=self.temperature,
        )

        logger.info(
            f"LLMHandler initialized | model={self.model}, temp={self.temperature}"
        )

    # ==================================================
    # MAIN CHAT INTERFACE
    # ==================================================

    def chat(self, prompt: str) -> str:
        """
        Generate a response from the LLM.
        Used by agent.py only.
        """
        try:
            response = self._llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "Sorry, I'm having trouble responding right now."

    # ==================================================
    # OPTIONAL HELPERS (IDEA FROM OLD PROJECT)
    # ==================================================

    def summarize(self, text: str) -> str:
        prompt = f"""
Summarize the following text clearly and concisely:

{text}
"""
        return self.chat(prompt)

    def classify(self, text: str, labels: list[str]) -> str:
        labels_str = ", ".join(labels)
        prompt = f"""
Classify the following text into one of these categories:
{labels_str}

Text:
{text}

Return only the category name.
"""
        return self.chat(prompt)
