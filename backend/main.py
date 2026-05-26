from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend import analyzer, embedder, parser
from backend.models import AnalyzeResponse


app = FastAPI(title="Resume Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "model": "mistral (ollama)",
        "embedder": "all-MiniLM-L6-v2",
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    file: UploadFile = File(...), job_description: str = Form(...)
) -> AnalyzeResponse:
    file_bytes = await file.read()

    try:
        resume_text = parser.extract_text_from_pdf(file_bytes)
        if not resume_text:
            raise HTTPException(422, "Could not extract text from PDF")

        chunks = parser.chunk_text(resume_text)
        collection = embedder.embed_and_store(chunks)
        result = analyzer.analyze_resume(collection, resume_text, job_description)

        return AnalyzeResponse(
            extracted_skills=result.get("extracted_skills", []),
            fit_score=result.get("fit_score", 0),
            missing_keywords=result.get("missing_keywords", []),
            suggestion=result.get("suggestion", ""),
            raw_resume_text=resume_text,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
