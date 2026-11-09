import asyncio
import time

from agents.langchain_agent import run_research


async def execute_research(question: str):
    start = time.perf_counter()

    report = await asyncio.to_thread(
        run_research,
        question
    )

    elapsed = time.perf_counter() - start

    return {
        "success": bool(report.strip()),
        "framework": "LangChain",
        "model": "qwen3:1.7b",
        "question": question,
        "report": report,
        "execution_time": round(elapsed, 2),
        "status": "completed" if report.strip() else "failed",
    }