import asyncio
import time
from typing import Any

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from dotenv import load_dotenv

from tools.research_tools import read_document, search_documents
from tools.websearch_tool import WebSearchSession

load_dotenv()

MODEL_NAME = "qwen3:1.7b"
OLLAMA_URL = "http://localhost:11434"
MAX_OUTPUT_TOKENS = 1600

SYSTEM_MESSAGE = """
You are an academic research assistant.

Answer the user's question accurately and directly. Use the local document
search and document reading tools when stored evidence is relevant. Use the web
search tool for current, recent, date-specific, or externally verifiable facts.
You may use both tool groups when useful, but avoid unnecessary calls.

Never invent citations, authors, dates, statistics, URLs, or tool results.
Distinguish retrieved evidence from your own explanation. If evidence is
insufficient, say so. Return a complete, focused answer and do not stop in the
middle of a sentence or section.
"""


def _search_documents(query: str) -> str:
    """Search the local research documents."""
    return str(search_documents.invoke({"query": query}))


def _read_document(document_id: str) -> str:
    """Read a local research document by its document ID."""
    return str(read_document.invoke({"document_id": document_id}))


def _extract_text(message: Any) -> str:
    content = getattr(message, "content", "")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(item["text"])
        return "\n".join(parts).strip()

    return ""


async def _run_autogen_research(question: str) -> str:
    search_session = WebSearchSession()
    model_client = OllamaChatCompletionClient(
        model=MODEL_NAME,
        host=OLLAMA_URL,
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "family": "unknown",
        },
        options={
            "temperature": 0.2,
            "num_predict": MAX_OUTPUT_TOKENS,
            "num_ctx": 8192,
        },
    )

    agent = AssistantAgent(
        name="autogen_researcher",
        model_client=model_client,
        tools=[
            _search_documents,
            _read_document,
            search_session.search,
        ],
        system_message=SYSTEM_MESSAGE,
        max_tool_iterations=3,
        reflect_on_tool_use=True,
    )

    try:
        result = await agent.run(task=question)
        for message in reversed(result.messages):
            report = _extract_text(message)
            if report:
                return report
        return "The AutoGen agent returned an empty response."
    finally:
        await model_client.close()


def run_autogen_research(question: str) -> str:
    """Run research with AutoGen and both local and web search tools."""
    start_time = time.perf_counter()
    print("[1/3] Initializing AutoGen research agent...", flush=True)
    print("[2/3] AutoGen agent has document and web search tools.", flush=True)

    report = asyncio.run(_run_autogen_research(question))

    print(
        f"[3/3] AutoGen execution time: "
        f"{time.perf_counter() - start_time:.2f}s",
        flush=True,
    )
    return report
