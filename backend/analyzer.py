import json
import re
import os
from groq import Groq
from dotenv import load_dotenv
from backend.embedder import retrieve_relevant_chunks

load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"

def call_groq(prompt: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return response.choices[0].message.content

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
    retrieved_chunks = retrieve_relevant_chunks(collection, job_description, n_results=5)
    retrieved_text = "\n".join(retrieved_chunks)

    prompt = f"""You are a JSON API. You must respond with ONLY a JSON object, nothing else. No explanation, no markdown, no code fences, no text before or after.

Resume:
{retrieved_text}

Job Description:
{job_description}

Respond with ONLY this exact JSON structure (fill in real values):
{{"extracted_skills": ["Python", "FastAPI"], "fit_score": 72, "missing_keywords": ["Docker", "RAG"], "suggestion": "Add more details about your ML project experience."}}"""

    raw = call_groq(prompt)
    text = clean_json_response(raw)

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
