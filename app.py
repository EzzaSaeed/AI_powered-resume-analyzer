import os
import json
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import OpenAI
from pypdf import PdfReader

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    st.error("OPENROUTER_API_KEY is missing. Add it to your .env file.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

# Change this to an OpenRouter model available to your account.
MODEL ="openai/gpt-oss-20b:free"


# ---------------------------------------------------------
# Structured Output Schema
# ---------------------------------------------------------

class ResumeAnalysis(BaseModel):
    score: int = Field(
        description="Overall ATS compatibility score from 0 to 100"
    )

    strengths: list[str] = Field(
        description="Important strengths of the candidate's resume"
    )

    missing_skills: list[str] = Field(
        description="Skills from the job description that appear to be missing"
    )

    weaknesses: list[str] = Field(
        description="Important weaknesses in the resume"
    )

    improvements: list[str] = Field(
        description="Specific and actionable resume improvements"
    )

    improved_bullets: list[str] = Field(
        description="Improved versions of weak resume bullet points"
    )


# ---------------------------------------------------------
# PDF Text Extraction
# ---------------------------------------------------------

def extract_pdf_text(uploaded_file):
    """Extract text from an uploaded PDF."""

    reader = PdfReader(uploaded_file)

    text = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text.append(page_text)

    return "\n".join(text)


# ---------------------------------------------------------
# AI Resume Analysis
# ---------------------------------------------------------

def analyze_resume(resume_text, job_description):

    system_prompt = """
You are an expert technical recruiter and ATS resume evaluator.

Your task is to analyze a candidate's resume against a job description.

Evaluate:

1. Overall ATS compatibility
2. Resume strengths
3. Missing skills
4. Resume weaknesses
5. Specific improvements
6. Improved versions of weak resume bullet points

Important rules:

- Do not invent experience, education, projects, or skills.
- Only use information contained in the resume.
- Compare the resume directly with the job description.
- Make recommendations specific and actionable.
- The score must be between 0 and 100.
- Keep the feedback professional and useful for a student or early-career developer.
"""

    user_prompt = f"""
RESUME:

{resume_text}


JOB DESCRIPTION:

{job_description}


Analyze this resume against the job description.
Return the result according to the required structured schema.
"""

    try:

        response = client.chat.completions.create(
            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            temperature=0.2,

            response_format={
                "type": "json_object"
            }
        )

        content = response.choices[0].message.content

        data = json.loads(content)

        return ResumeAnalysis.model_validate(data)

    except Exception as e:

        st.error(f"AI analysis failed: {e}")
        return None


# ---------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer")

st.write(
    "Analyze your resume against a job description using AI "
    "and get actionable ATS-focused feedback."
)

st.divider()


# ---------------------------------------------------------
# Input Section
# ---------------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("📎 Upload Resume")

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf"]
    )

with right:

    st.subheader("💼 Job Description")

    job_description = st.text_area(
        "Paste the job description here",
        height=250,
        placeholder="Paste the complete job description..."
    )


st.divider()


# ---------------------------------------------------------
# Analyze Button
# ---------------------------------------------------------

if st.button(
    "🚀 Analyze Resume",
    use_container_width=True
):

    if uploaded_file is None:

        st.warning("Please upload your resume PDF.")

    elif not job_description.strip():

        st.warning("Please enter the job description.")

    else:

        with st.spinner("Analyzing your resume..."):

            resume_text = extract_pdf_text(uploaded_file)

            if not resume_text.strip():

                st.error(
                    "Could not extract text from this PDF. "
                    "Try a text-based PDF."
                )

            else:

                result = analyze_resume(
                    resume_text,
                    job_description
                )

                if result:

                    st.session_state["analysis"] = result


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

if "analysis" in st.session_state:

    result = st.session_state["analysis"]

    st.divider()

    st.header("📊 Resume Analysis")


    # ATS Score

    st.subheader("ATS Compatibility Score")

    st.metric(
        label="Overall Score",
        value=f"{result.score}/100"
    )

    st.progress(
        min(max(result.score, 0), 100) / 100
    )


    # Three-column summary

    col1, col2, col3 = st.columns(3)

    with col1:

        st.subheader("✅ Strengths")

        for item in result.strengths:

            st.write(f"• {item}")


    with col2:

        st.subheader("⚠️ Missing Skills")

        for item in result.missing_skills:

            st.write(f"• {item}")


    with col3:

        st.subheader("🔍 Weaknesses")

        for item in result.weaknesses:

            st.write(f"• {item}")


    st.divider()


    # Improvements

    st.subheader("💡 Recommended Improvements")

    for index, item in enumerate(
        result.improvements,
        start=1
    ):

        st.write(
            f"**{index}.** {item}"
        )


    st.divider()


    # Improved bullets

    st.subheader("✍️ Improved Resume Bullets")

    for bullet in result.improved_bullets:

        st.info(bullet)


    st.divider()


    # Download JSON

    result_json = json.dumps(
        result.model_dump(),
        indent=2
    )

    st.download_button(
        label="⬇️ Download Analysis as JSON",
        data=result_json,
        file_name="resume_analysis.json",
        mime="application/json"
    )