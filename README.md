# Agent Research API

A local academic research assistant built with FastAPI, LangChain, and Ollama. It uses the `qwen3:1.7b` model to answer open-ended research questions and can retrieve information from local research documents.

## Requirements

- Python 3.10 or newer
- [Ollama](https://ollama.com/)
- The `qwen3:1.7b` Ollama model

## Setup

1. Start Ollama and download the model:

   ```bash
   ollama pull qwen3:1.7b
   ```

2. Create and activate a virtual environment from the repository root:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the backend dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

4. Start the API:

   ```bash
   cd backend
   uvicorn main:app --reload
   ```

The API is available at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`.

## API

### Health check

```bash
curl http://localhost:8000/api/health
```

This reports whether the API can connect to Ollama.

### Run research

The `question` must contain between 10 and 2,000 characters.

```bash
curl -X POST http://localhost:8000/api/research/run \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the main security challenges in federated learning?"}'
```

The response includes the generated report, execution time, model, and completion status.

## Project Structure

```text
backend/
├── agents/       LangChain agent and research orchestration
├── core/         Ollama client configuration
├── datasets/     Local research documents
├── schemas/      API request and response models
├── services/     Research execution service
├── tools/        Document search and reading tools
└── main.py       FastAPI application
frontend/         Frontend workspace (not implemented yet)
```

## Development

Run the backend from the `backend` directory so Python can resolve the application modules:

```bash
cd backend
uvicorn main:app --reload
```

The local API enables permissive CORS for development. Configure `allow_origins` in `backend/main.py` before deploying it outside a trusted local environment.
