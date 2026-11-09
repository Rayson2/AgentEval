
from pydantic import BaseModel, Field
from typing import Optional


class ResearchRequest(BaseModel):
    question: str = Field(
        min_length=10,
        max_length=2000,
        description="Open-ended research question"
    )


class ResearchResponse(BaseModel):
    success: bool
    framework: str
    model: str
    question: str
    report: str
    execution_time: float
    status: str


class HealthResponse(BaseModel):
    status: str
    framework: str
    model: str
    ollama: str
