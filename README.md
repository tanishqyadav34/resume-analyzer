# Resume Analyzer & Job Fit Scorer
> 100% Free & Local - No API keys required

## How it works
PDF -> text extraction -> chunking -> local embeddings (sentence-transformers) -> ChromaDB -> semantic retrieval -> Mistral via Ollama -> JSON output -> fit score

## Prerequisites
1. Python 3.10+
2. Install Ollama: https://ollama.com
3. Run: ollama pull mistral

## Setup
1. pip install -r requirements.txt
2. uvicorn backend.main:app --reload --port 8000
3. streamlit run frontend/app.py

## Tech Stack
| Component | Tool | Cost |
|-----------|------|------|
| LLM | Mistral via Ollama | Free |
| Embeddings | sentence-transformers | Free |
| Vector DB | ChromaDB in-memory | Free |
| Backend | FastAPI | Free |
| Frontend | Streamlit | Free |
![Output Screenshot](assets/output.png)
