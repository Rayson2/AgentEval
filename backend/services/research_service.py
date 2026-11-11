import asyncio
import time

from agents.crewai_agent import run_crewai_research
from agents.autogen_agent import run_autogen_research
from agents.langchain_agent import run_research
from core.settings import MODEL_NAME


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
        "model": MODEL_NAME,
        "question": question,
        "report": report,
        "execution_time": round(elapsed, 2),
        "status": "completed" if report.strip() else "failed",
    }


async def execute_crewai_research(question: str):
    start = time.perf_counter()

    report = await asyncio.to_thread(
        run_crewai_research,
        question
    )

    elapsed = time.perf_counter() - start

    return {
        "success": bool(report.strip()),
        "framework": "CrewAI",
        "model": MODEL_NAME,
        "question": question,
        "report": report,
        "execution_time": round(elapsed, 2),
        "status": "completed" if report.strip() else "failed",
    }


async def execute_autogen_research(question: str):
    start = time.perf_counter()

    report = await asyncio.to_thread(
        run_autogen_research,
        question
    )

    elapsed = time.perf_counter() - start

    return {
        "success": bool(report.strip()),
        "framework": "AutoGen",
        "model": MODEL_NAME,
        "question": question,
        "report": report,
        "execution_time": round(elapsed, 2),
        "status": "completed" if report.strip() else "failed",
    }