"""
    API wrapper around ollama
"""

from .api import generate_chat_completion
from .dto import OllamaChat, OllamaChatMessage

__all__ = ["generate_chat_completion", "OllamaChat", "OllamaChatMessage"]
