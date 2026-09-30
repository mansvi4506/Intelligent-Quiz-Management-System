"""Shared Groq client configuration for quiz generation and explanations."""

from django.conf import settings
from openai import OpenAI


def get_ai_client():
    """Return an OpenAI-compatible client configured for Groq."""
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to the .env file.")

    return OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url=settings.GROQ_API_BASE_URL,
    )
