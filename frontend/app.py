import requests
import streamlit as st


BACKEND_URL = "http://localhost:8000/analyze"


st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.title("Resume Analyzer & Job Fit Scorer")
st.caption("Runs 100% locally - no API keys, no cost")

left_col, right_col = st.columns([1, 1])

with left_col:
    uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

with right_col:
    job_description = st.text_area("Paste Job Description", height=300)

if st.button("Analyze Resume", use_container_width=True):
    if not uploaded_file or not job_description:
        st.warning("Please upload a PDF and enter a job description")
    else:
        with st.spinner(
            "Analyzing locally with Mistral... this may take 30-90 seconds on CPU"
        ):
            response = requests.post(
                BACKEND_URL,
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf",
                    )
                },
                data={"job_description": job_description},
                timeout=600
            )

        if response.status_code == 200:
            result = response.json()
            score = result.get("fit_score", 0)

            if score > 70:
                st.success(f"Fit Score: {score}/100")
            elif 40 <= score <= 70:
                st.warning(f"Fit Score: {score}/100")
            else:
                st.error(f"Fit Score: {score}/100")

            st.subheader("Extracted Skills")
            skills = result.get("extracted_skills", [])
            if skills:
                st.markdown(" ".join(f"`{skill}`" for skill in skills))

            st.subheader("Missing Keywords")
            for keyword in result.get("missing_keywords", []):
                st.markdown(f"- {keyword}")

            st.info(result.get("suggestion", ""))

            with st.expander("Raw Extracted Resume Text"):
                st.text(result.get("raw_resume_text", ""))
        else:
            try:
                detail = response.json().get("detail", "Unknown error")
            except ValueError:
                detail = "Unknown error"
            st.error(f"Error: {detail}")
            st.caption("Make sure Ollama is running: ollama serve")

