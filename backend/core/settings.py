import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _get_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _get_float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


MODEL_NAME = os.getenv("MODEL_NAME", "qwen3:1.7b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
LLM_TEMPERATURE = _get_float("LLM_TEMPERATURE", 0.2)
MAX_OUTPUT_TOKENS = _get_int("MAX_OUTPUT_TOKENS", 1600)
CONTEXT_WINDOW_SIZE = _get_int("CONTEXT_WINDOW_SIZE", 8192)
LANGCHAIN_CONTEXT_SIZE = _get_int("LANGCHAIN_CONTEXT_SIZE", 2048)
LANGCHAIN_OUTPUT_TOKENS = _get_int("LANGCHAIN_OUTPUT_TOKENS", 250)
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "5m")
MAX_SEARCH_CALLS = _get_int("MAX_SEARCH_CALLS", 2)
SERPER_RESULTS = _get_int("SERPER_RESULTS", 2)
SERPER_COUNTRY = os.getenv("SERPER_COUNTRY", "in")
SERPER_LOCALE = os.getenv("SERPER_LOCALE", "en-IN")
