"""Scrapers for different LLM model providers."""

from .base import BaseScraper
from .ollama import OllamaScraper
from .huggingface import HuggingFaceScraper

__all__ = ["BaseScraper", "OllamaScraper", "HuggingFaceScraper"]
