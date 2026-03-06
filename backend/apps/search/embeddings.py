import logging
import ollama
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_embedding(text):
    response = ollama.embed(
        model=settings.OLLAMA_EMBED_MODEL,
        input=text,
    )
    return response.embeddings[0]
