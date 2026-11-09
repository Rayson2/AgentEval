from langchain_ollama import ChatOllama

# MODEL_NAME = "qwen3:4b"
MODEL_NAME = "qwen3:1.7b"

def get_llm():
    return ChatOllama(
        model=MODEL_NAME,
        base_url="http://localhost:11434",
        temperature=0.2,
        reasoning=False,
        num_ctx=2048,
        num_predict=250,
        keep_alive="5m",
    )




