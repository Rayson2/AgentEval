from langchain_ollama import ChatOllama

from core.settings import (
	LANGCHAIN_CONTEXT_SIZE,
	LANGCHAIN_OUTPUT_TOKENS,
	LLM_TEMPERATURE,
	MODEL_NAME,
	OLLAMA_KEEP_ALIVE,
	OLLAMA_URL,
)

def get_llm():
    return ChatOllama(
        model=MODEL_NAME,
        base_url=OLLAMA_URL,
        temperature=LLM_TEMPERATURE,
        reasoning=False,
        num_ctx=LANGCHAIN_CONTEXT_SIZE,
        num_predict=LANGCHAIN_OUTPUT_TOKENS,
        keep_alive=OLLAMA_KEEP_ALIVE,
    )




