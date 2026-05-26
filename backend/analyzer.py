import json
import re

import requests

from backend.embedder import retrieve_relevant_chunks


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"


def call_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=600,
        )
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Ollama is not running. Please start it: ollama serve"
        ) from exc

    return response.json()["response"]


def clean_json_response(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    return text


def analyze_resume(collection, resume_text: str, job_description: str) -> dict:
    retrieved_chunks = retrieve_relevant_chunks(
        collection, job_description, n_results=5
    )
    retrieved_text = "\n".join(retrieved_chunks)

    prompt = f"""You are a JSON API. You must respond with ONLY a JSON object, nothing else. No explanation, no markdown, no code fences, no text before or after.

Resume:
{retrieved_text}

Job Description:
{job_description}

Respond with ONLY this exact JSON structure (fill in real values):
{{"extracted_skills": ["Python", "FastAPI"], "fit_score": 72, "missing_keywords": ["Docker", "RAG"], "suggestion": "Add more details about your ML project experience."}}"""

    text = clean_json_response(call_ollama(prompt))

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    return {
        "extracted_skills": [],
        "fit_score": 0,
        "missing_keywords": [],
        "suggestion": "Could not parse model response. Please try again.",
    }