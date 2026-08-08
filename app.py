import os
import json

import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import OpenAI
from pypdf import PdfReader


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    st.error(
        "OPENROUTER_API_KEY is missing. "
        "Add it to Streamlit Secrets or your .env file."
    )
    st.stop()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

# You can change this model if it is unavailable on OpenRouter.
MODEL = "openai/gpt-oss-20b:free"


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# =========================================================
# STRUCTURED OUTPUT SCHEMA
# =========================================================

class ResumeAnalysis(BaseModel):

    score: int = Field(
        ge=0,
        le=100,
        description="ATS compatibility score from 0 to 100"
    )

    strengths: list[str] = Field(
        default_factory=list,
        description="Strengths found in the resume"
    )

    missing_skills: list[str] = Field(
        default_factory=list,
        description="Skills required by the job but missing from the resume"
    )

    weaknesses: list[str] = Field(
        default_factory=list,
        description="Important weaknesses in the resume"
    )

    improvements: list[str] = Field(
        default_factory=list,
        description="Specific resume improvement suggestions"
    )

    improved_bullets: list[str] = Field(
        default_factory=list,
        description="Improved versions of resume bullet points"
    )


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf_text(uploaded_file):

    try:

        reader = PdfReader(uploaded_file)

        pages_text = []

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                pages_text.append(page_text)

        return "\n".join(pages_text).strip()

    except Exception as e:

        st.error(f"Could not read the PDF: {e}")

        return ""


# =========================================================
# CLEAN AI RESPONSE
# =========================================================

def clean_json_response(content):

    if not content:
        raise ValueError("The AI returned an empty response.")

    content = content.strip()

    # Remove markdown JSON code fences
    if content.startswith("```json"):

        content = content[7:]

    elif content.startswith("```"):

        content = content[3:]

    if content.endswith("```"):

        content = content[:-3]

    content = content.strip()

    # Sometimes models return extra text before/after JSON.
    # Try to extract the JSON object.
    first_brace = content.find("{")
    last_brace = content.rfind("}")

    if first_brace != -1 and last_brace != -1:

        content = content[first_brace:last_brace + 1]

    return content


# =========================================================
# AI RESUME ANALYSIS
# =========================================================

def analyze_resume(resume_text, job_description):

    system_prompt = """
You are an expert technical recruiter and ATS resume evaluator.

Your job is to compare a candidate's resume against a target
job description.

Evaluate:

1. ATS compatibility score
2. Resume strengths
3. Missing skills
4. Resume weaknesses
5. Specific improvement suggestions
6. Improved resume bullet points

IMPORTANT RULES:

- Do NOT invent experience.
- Do NOT invent projects.
- Do NOT invent education.
- Do NOT claim that the candidate has a skill unless it appears
  in the resume.
- Base your analysis only on the provided resume and job description.
- Be useful for students and early-career developers.
- Keep recommendations specific and actionable.
- The score must be between 0 and 100.
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not add explanations outside the JSON object.
"""

    user_prompt = f"""
Analyze the following resume against the following job description.

========================
RESUME
========================

{resume_text}

========================
JOB DESCRIPTION
========================

{job_description}

========================
REQUIRED JSON FORMAT
========================

Return ONLY a JSON object using exactly these fields:

{{
    "score": 0,
    "strengths": [
        "example"
    ],
    "missing_skills": [
        "example"
    ],
    "weaknesses": [
        "example"
    ],
    "improvements": [
        "example"
    ],
    "improved_bullets": [
        "example"
    ]
}}

Make the score an integer between 0 and 100.
"""

    content = ""

    try:

        # -------------------------------------------------
        # OpenRouter API request
        # -------------------------------------------------

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

            max_tokens=2500
        )

        # -------------------------------------------------
        # Extract AI response
        # -------------------------------------------------

        if not response.choices:

            raise ValueError(
                "The AI API returned no choices."
            )

        message = response.choices[0].message

        content = message.content

        # -------------------------------------------------
        # Check empty response
        # -------------------------------------------------

        if not content:

            raise ValueError(
                "The AI returned an empty response."
            )

        # -------------------------------------------------
        # Clean response
        # -------------------------------------------------

        cleaned_content = clean_json_response(content)

        # -------------------------------------------------
        # Parse JSON
        # -------------------------------------------------

        data = json.loads(cleaned_content)

        # -------------------------------------------------
        # Validate with Pydantic
        # -------------------------------------------------

        result = ResumeAnalysis.model_validate(data)

        return result

    except json.JSONDecodeError as e:

        st.error(
            f"The AI returned invalid JSON: {e}"
        )

        with st.expander("Show AI response for debugging"):

            st.code(
                content if content else "Empty response"
            )

        return None

    except Exception as e:

        st.error(
            f"AI analysis failed: {e}"
        )

        with st.expander("Show technical details"):

            st.write(str(e))

            if content:

                st.code(content)

        return None


# =========================================================
# HEADER
# =========================================================

st.title("📄 AI Resume Analyzer")

st.markdown(
    """
### Optimize your resume for your target job

Upload your resume and paste a job description to receive
AI-powered ATS analysis, missing skills, weaknesses,
improvement suggestions, and improved resume bullets.
"""
)

st.divider()


# =========================================================
# INPUT SECTION
# =========================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader("📎 Upload Resume")

    uploaded_file = st.file_uploader(
        "Upload your resume as a PDF",
        type=["pdf"]
    )


with col2:

    st.subheader("💼 Job Description")

    job_description = st.text_area(
        "Paste the target job description",
        height=250,
        placeholder=(
            "Example:\n\n"
            "We are looking for an AI Intern with "
            "Python, APIs, prompt engineering..."
        )
    )


st.divider()


# =========================================================
# ANALYZE BUTTON
# =========================================================

analyze_button = st.button(
    "🚀 Analyze Resume",
    type="primary",
    use_container_width=True
)


if analyze_button:

    # -----------------------------------------------------
    # Validate resume
    # -----------------------------------------------------

    if uploaded_file is None:

        st.warning(
            "Please upload your resume PDF first."
        )

        st.stop()


    # -----------------------------------------------------
    # Validate job description
    # -----------------------------------------------------

    if not job_description.strip():

        st.warning(
            "Please paste a job description first."
        )

        st.stop()


    # -----------------------------------------------------
    # Extract resume text
    # -----------------------------------------------------

    with st.spinner("Reading your resume..."):

        resume_text = extract_pdf_text(
            uploaded_file
        )


    if not resume_text:

        st.error(
            "No readable text was found in the PDF. "
            "Please upload a text-based PDF."
        )

        st.stop()


    # -----------------------------------------------------
    # Analyze resume
    # -----------------------------------------------------

    with st.spinner(
        "AI is analyzing your resume against the job description..."
    ):

        result = analyze_resume(
            resume_text,
            job_description
        )


    # -----------------------------------------------------
    # Save result
    # -----------------------------------------------------

    if result:

        st.session_state["analysis"] = result


# =========================================================
# RESULTS
# =========================================================

if "analysis" in st.session_state:

    result = st.session_state["analysis"]

    st.divider()

    st.header("📊 Resume Analysis")


    # =====================================================
    # SCORE
    # =====================================================

    st.subheader("🎯 ATS Compatibility Score")

    score_col1, score_col2 = st.columns(
        [1, 3]
    )


    with score_col1:

        st.metric(
            "ATS Score",
            f"{result.score}/100"
        )


    with score_col2:

        st.progress(
            result.score / 100
        )


    st.divider()


    # =====================================================
    # STRENGTHS / MISSING SKILLS / WEAKNESSES
    # =====================================================

    col1, col2, col3 = st.columns(3)


    # -----------------------------------------------------
    # Strengths
    # -----------------------------------------------------

    with col1:

        st.subheader("✅ Strengths")

        if result.strengths:

            for item in result.strengths:

                st.success(
                    f"• {item}"
                )

        else:

            st.write(
                "No major strengths identified."
            )


    # -----------------------------------------------------
    # Missing skills
    # -----------------------------------------------------

    with col2:

        st.subheader("⚠️ Missing Skills")

        if result.missing_skills:

            for item in result.missing_skills:

                st.warning(
                    f"• {item}"
                )

        else:

            st.write(
                "No major missing skills identified."
            )


    # -----------------------------------------------------
    # Weaknesses
    # -----------------------------------------------------

    with col3:

        st.subheader("🔍 Weaknesses")

        if result.weaknesses:

            for item in result.weaknesses:

                st.error(
                    f"• {item}"
                )

        else:

            st.write(
                "No major weaknesses identified."
            )


    st.divider()


    # =====================================================
    # IMPROVEMENTS
    # =====================================================

    st.subheader("💡 Recommended Improvements")

    if result.improvements:

        for index, item in enumerate(
            result.improvements,
            start=1
        ):

            st.write(
                f"**{index}.** {item}"
            )

    else:

        st.write(
            "No specific improvements were generated."
        )


    st.divider()


    # =====================================================
    # IMPROVED BULLETS
    # =====================================================

    st.subheader("✍️ Improved Resume Bullets")

    if result.improved_bullets:

        for bullet in result.improved_bullets:

            st.info(bullet)

    else:

        st.write(
            "No improved bullet points were generated."
        )


    st.divider()


    # =====================================================
    # DOWNLOAD JSON
    # =====================================================

    st.subheader("📥 Export Analysis")

    result_json = json.dumps(
        result.model_dump(),
        indent=4
    )

    st.download_button(
        label="⬇️ Download Analysis as JSON",
        data=result_json,
        file_name="resume_analysis.json",
        mime="application/json",
        use_container_width=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Resume Analyzer • Built with Python, Streamlit, "
    "OpenRouter and Pydantic"
)