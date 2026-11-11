
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.settings import MODEL_NAME, OLLAMA_URL
from schemas.research import ResearchRequest, ResearchResponse
from services.research_service import (
    execute_autogen_research,
    execute_crewai_research,
    execute_research,
)


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Agent Research API...")
    yield
    print("Shutting down Agent Research API...")


# FastAPI application
app = FastAPI(
    title="Local Agent Research API",
    description="Open-ended research using LangChain and Qwen3",
    version="1.0.0",
    lifespan=lifespan
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Root endpoint
@app.get("/")
async def root():
    return {
        "application": "Local Agent Research API",
        "status": "running",
        "framework": "LangChain",
        "model": MODEL_NAME
    }


# Health check endpoint
@app.get("/api/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(
                f"{OLLAMA_URL}/api/tags"
            )
            response.raise_for_status()

        return {
            "status": "healthy",
            "framework": "LangChain",
            "model": MODEL_NAME,
            "ollama": "connected"
        }

    except Exception:
        return {
            "status": "degraded",
            "framework": "LangChain",
            "model": MODEL_NAME,
            "ollama": "disconnected"
        }


# Research endpoint
@app.post(
    "/api/research/langchain",
    response_model=ResearchResponse,
    tags=["Research"]
)
async def run_langchain_research_endpoint(request: ResearchRequest):

    try:
        result = await execute_research(request.question)
        return result

    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Research exceeded the 25-second execution deadline."
        )

    except Exception as error:
        print("Research API error:", repr(error))

        raise HTTPException(
            status_code=500,
            detail="Research execution failed."
        )


@app.post(
    "/api/research/crewai",
    response_model=ResearchResponse,
    tags=["Research"]
)
async def run_crewai_research_endpoint(request: ResearchRequest):

    try:
        result = await execute_crewai_research(request.question)
        return result

    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Research exceeded the 25-second execution deadline."
        )

    except Exception as error:
        print("CrewAI research API error:", repr(error))

        raise HTTPException(
            status_code=500,
            detail="CrewAI research execution failed."
        )


@app.post(
    "/api/research/autogen",
    response_model=ResearchResponse,
    tags=["Research"]
)
async def run_autogen_research_endpoint(request: ResearchRequest):

    try:
        result = await execute_autogen_research(request.question)
        return result

    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Research exceeded the 25-second execution deadline."
        )

    except Exception as error:
        print("AutoGen research API error:", repr(error))

        raise HTTPException(
            status_code=500,
            detail="AutoGen research execution failed."
        )
