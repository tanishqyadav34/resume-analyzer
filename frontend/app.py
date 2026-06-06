import os

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/analyze")


st.set_page_config(
    page_title="ResumeIQ — Job Fit Analyzer",
    page_icon="🎯",
    layout="wide"
)

st.markdown("""
<style>
    /* Clean background */
    .stApp { background-color: #F8F9FB; }
    
    /* Hide default streamlit header/footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container padding */
    .block-container { padding-top: 2.5rem; padding-bottom: 2rem; }

    /* Hero section */
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.6rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.5px;
        margin-bottom: 0.3rem;
    }
    .hero-sub {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 2rem;
    }

    /* Score card */
    .score-card {
        background: linear-gradient(135deg, #1E3A5F 0%, #2E6DA4 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .score-number {
        font-size: 4rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -2px;
    }
    .score-label {
        font-size: 0.95rem;
        opacity: 0.85;
        margin-top: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Skill tags */
    .skill-tag {
        display: inline-block;
        background: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 3px;
    }

    /* Missing keyword tags */
    .missing-tag {
        display: inline-block;
        background: #FFF7ED;
        color: #C2410C;
        border: 1px solid #FED7AA;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 3px;
    }

    /* Section headers */
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #0F172A;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.8rem;
        margin-top: 1.2rem;
    }

    /* Suggestion box */
    .suggestion-box {
        background: #F0FDF4;
        border-left: 4px solid #16A34A;
        border-radius: 0 10px 10px 0;
        padding: 1rem 1.2rem;
        color: #14532D;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Upload area styling */
    .upload-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.4rem;
    }

    /* Analyze button */
    .stButton > button {
        background: linear-gradient(135deg, #1E3A5F, #2E6DA4);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        transition: opacity 0.2s;
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        opacity: 0.9;
        color: white;
        border: none;
    }

    /* Divider */
    hr { border-color: #E2E8F0; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="hero-title">🎯 ResumeIQ</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Analyze your resume against any job description using AI — get a fit score, skill gaps, and actionable suggestions.</p>', unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns([1, 1], gap="large")
with col1:
    st.markdown('<p class="upload-label">📄 Upload Resume (PDF)</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

with col2:
    st.markdown('<p class="upload-label">📋 Job Description</p>', unsafe_allow_html=True)
    job_description = st.text_area("", height=280, placeholder="Paste the full job description here...", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)
analyze_clicked = st.button("Analyze Resume →")

if analyze_clicked:
    if not uploaded_file or not job_description:
        st.warning("Please upload a PDF and enter a job description")
    else:
        with st.spinner(
            "Analyzing with AI — extracting skills and computing fit score..."
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
            if score >= 70:
                score_color = "#22C55E"
                verdict = "Strong Match"
            elif score >= 40:
                score_color = "#F59E0B"
                verdict = "Partial Match"
            else:
                score_color = "#EF4444"
                verdict = "Needs Work"

            st.markdown(f"""
<div class="score-card">
    <div class="score-number" style="color:{score_color}">{score}</div>
    <div style="font-size:1.1rem;margin-top:0.3rem;">/100 — <strong>{verdict}</strong></div>
    <div class="score-label">Job Fit Score</div>
</div>
""", unsafe_allow_html=True)

            skills = result.get("extracted_skills", [])
            if skills:
                st.markdown('<p class="section-title">✅ Skills Found in Resume</p>', unsafe_allow_html=True)
                tags_html = "".join([f'<span class="skill-tag">{s}</span>' for s in skills])
                st.markdown(tags_html, unsafe_allow_html=True)

            missing = result.get("missing_keywords", [])
            if missing:
                st.markdown('<p class="section-title">⚠️ Missing Keywords</p>', unsafe_allow_html=True)
                missing_html = "".join([f'<span class="missing-tag">{m}</span>' for m in missing])
                st.markdown(missing_html, unsafe_allow_html=True)

            suggestion = result.get("suggestion", "")
            if suggestion:
                st.markdown('<p class="section-title">💡 Improvement Suggestion</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="suggestion-box">{suggestion}</div>', unsafe_allow_html=True)

            with st.expander("📄 View Extracted Resume Text"):
                st.text(result.get("raw_resume_text", ""))
        else:
            try:
                error_message = response.json().get("detail", "Unknown error")
            except ValueError:
                error_message = "Unknown error"
            st.markdown(f"""
<div style="background:#FEF2F2;border-left:4px solid #EF4444;border-radius:0 10px 10px 0;
padding:1rem 1.2rem;color:#7F1D1D;margin-top:1rem;">
⚠️ <strong>Error:</strong> {error_message}
</div>
""", unsafe_allow_html=True)
