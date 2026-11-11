# Agent Research API

A local academic research assistant built with **FastAPI, LangChain, CrewAI, AutoGen, and Ollama**. The project evaluates agent frameworks on open-ended research questions without a single ground-truth answer.

It uses the locally hosted `qwen3:1.7b` model through Ollama. LangChain uses local research documents, while CrewAI and AutoGen can use local documents and bounded Serper-powered web search.

## Features

- Local LLM inference using Ollama.
- FastAPI backend with REST API endpoints.
- LangChain-based research using local documents.
- CrewAI integration for web-based research using Serper.
- AutoGen integration with local document and web-search tools.
- Execution-time measurement for framework evaluation.
- Interactive API documentation through Swagger UI.

## Requirements

- Python 3.11 (recommended)
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/)
- `qwen3:1.7b` Ollama model
- Serper API key for CrewAI and AutoGen web search

> **Note:** Use Python 3.11 for CrewAI compatibility. Python 3.14 is not currently supported by the CrewAI installation requirements.

## Setup

### 1. Install and start Ollama

Install Ollama, start its service, and download the model:

```bash
ollama pull qwen3:1.7b
```

Verify that the model is available:

```bash
ollama list
```

### 2. Create the Python environment

From the repository root:

```bash
uv python install 3.11
uv venv --python 3.11 .venv
source .venv/bin/activate
```

Verify the Python version:

```bash
python --version
```

### 3. Install backend dependencies

```bash
uv pip install --upgrade pip
uv pip install -r backend/requirements.txt
```

### 4. Install CrewAI dependencies

Install CrewAI library inside the activated virtual environment:

```bash
uv pip install crewai crewai-tools
```

Verify the installation:

```bash
python -c "import crewai; print('CrewAI:', crewai.__version__)"
python -c "from crewai_tools import SerperDevTool; print('Serper: OK')"
python -c "from crewai import LLM; print('LLM integration: OK')"
```

AutoGen dependencies are installed from `backend/requirements.txt`. Verify the
installation with:

```bash
python -c "from autogen_agentchat.agents import AssistantAgent; print('AutoGen: OK')"
python -c "from autogen_ext.models.ollama import OllamaChatCompletionClient; print('AutoGen Ollama: OK')"
```

### 5. Configure Serper API

Create a `.env` file inside the `backend/` directory:

```env
SERPER_API_KEY=your_serper_api_key
```

Replace the placeholder with your actual API key.

Do not commit `.env` or expose your API key in source code. Ensure it is included in `.gitignore`.

### 6. Start the API

```bash
cd backend
uvicorn main:app --reload
```

The API is available at:

- API: http://localhost:8000
- Swagger documentation: http://localhost:8000/docs

## API

### Health check

```bash
curl http://localhost:8000/api/health
```

Checks whether the API can connect to Ollama.

### Run research

The API exposes one endpoint for each framework:

```http
POST /api/research/langchain
POST /api/research/crewai
POST /api/research/autogen
```

The `question` must contain between 10 and 2,000 characters.

Example:

```bash
curl -X POST http://localhost:8000/api/research/autogen \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the main security challenges in federated learning?"}'
```

The response includes:

- Generated research report
- Framework name
- Model name
- Execution time
- Completion status

## Project Structure

```text
agenteval/
├── backend/
│   ├── agents/
│   │   ├── langchain_agent.py
│   │   ├── crewai_agent.py
│   │   └── autogen_agent.py
│   ├── core/
│   │   └── ollama_client.py
│   ├── datasets/
│   │   └── documents/
│   ├── schemas/
│   │   └── research.py
│   ├── services/
│   │   └── research_service.py
│   ├── tools/
│   │   ├── research_tools.py
│   │   └── websearch_tool.py
│   ├── .env
│   ├── requirements.txt
│   └── main.py
├── frontend/
└── README.md
```

## Development

Always activate the virtual environment before running the backend:

```bash
source .venv/bin/activate
```

Run the API from the backend directory:

```bash
cd backend
uvicorn main:app --reload
```


## Evaluation Considerations

The project compares agent frameworks on open-ended research tasks.

Important evaluation metrics include:

- **Response quality:** Relevance, completeness, and factual accuracy.
- **Execution time:** Total time required to generate the report.
- **Tool usage:** Effectiveness of document retrieval and web search.
- **Source quality:** Credibility and relevance of supporting information.
- **Consistency:** Stability across repeated research questions.

For a fair comparison, use equivalent research questions, model settings, output limits, and retrieval capabilities. Local-document retrieval and web search should be evaluated separately or made equivalent across frameworks.

## Development Notes

- Ollama runs locally at `http://localhost:11434`.
- The default model is `qwen3:1.7b`.
- Keep the model and generation settings consistent across framework evaluations.
- The API currently uses permissive CORS settings for local development.
- Configure `allow_origins` in `backend/main.py` before deployment outside a trusted local environment.
- Do not expose the local API or Ollama service publicly without appropriate security controls.
