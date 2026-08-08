
📄 AI Resume Analyzer

An AI-powered resume analysis tool that evaluates a candidate's resume against a specific job description and provides actionable, ATS-focused feedback.

The application uses LLM-powered analysis, prompt engineering, API integration, and structured JSON validation to turn an unstructured resume into a clear and useful improvement report.

---

🚀 Project Overview

Job seekers often struggle to understand whether their resume matches a particular job description.

The AI Resume Analyzer solves this problem by allowing users to:

1. Upload their resume as a PDF.
2. Paste a target job description.
3. Analyze the resume using an AI model.
4. Receive a structured analysis.
5. Identify missing skills and weaknesses.
6. Get specific suggestions for improving the resume.
7. Generate improved versions of resume bullet points.
8. Download the analysis as a JSON file.

---

✨ Features

- 📎 PDF resume upload
- 💼 Job description input
- 🤖 AI-powered resume analysis
- 📊 ATS compatibility score
- ✅ Resume strengths
- ⚠️ Missing skills
- 🔍 Resume weaknesses
- 💡 Actionable improvement suggestions
- ✍️ Improved resume bullet points
- 📦 Structured JSON output
- ✔️ Pydantic response validation
- ⬇️ Downloadable analysis
- 🔐 API key stored securely using environment variables

---

🧠 AI Workflow

             User
              │
              ▼
       Upload Resume PDF
              │
              +
              │
       Paste Job Description
              │
              ▼
       Streamlit Application
              │
              ▼
       Extract PDF Text
              │
              ▼
        Prompt Engineering
              │
              ▼
        OpenRouter API
              │
              ▼
        AI Model Response
              │
              ▼
        JSON Validation
          with Pydantic
              │
              ▼
       Analysis Dashboard
              │
       ┌──────┼────────┐
       ▼      ▼        ▼
      ATS   Skills   Improvements
      Score Missing   & Bullets

---

🛠️ Tech Stack

Technology| Purpose
Python| Core programming language
Streamlit| Web interface
OpenRouter| LLM API access
OpenAI Python SDK| API communication
Pydantic| Structured output validation
pypdf| PDF text extraction
python-dotenv| Environment variable management

---

📁 Project Structure

AI-Resume-Analyzer/
│
├── app.py
├── requirements.txt
├── README.md
├── .env
└── .gitignore

«⚠️ The ".env" file contains the API key and must never be uploaded to GitHub.»

---



🔑 API Configuration

Create a ".env" file in the root directory:

OPENROUTER_API_KEY=your_api_key_here

Replace "your_api_key_here" with your OpenRouter API key.

The application reads the key using:

os.getenv("OPENROUTER_API_KEY")

This keeps the API key outside the source code.

---

▶️ Running the Application

Start the Streamlit application:

streamlit run app.py

The application will open in your browser.



🧩 Prompt Engineering

The application uses a dedicated system prompt that instructs the AI to behave as an expert technical recruiter and ATS evaluator.

The prompt establishes:

- The AI's role
- Evaluation criteria
- Required analysis areas
- Restrictions against inventing candidate experience
- Requirements for actionable recommendations
- Structured response requirements

This helps produce more consistent and relevant results than a simple prompt such as:

Analyze this resume.

---

📦 Structured Output

One of the main technical features of this project is structured AI output.

The expected response is represented using a Pydantic model:

class ResumeAnalysis(BaseModel):
    score: int
    strengths: list[str]
    missing_skills: list[str]
    weaknesses: list[str]
    improvements: list[str]
    improved_bullets: list[str]

The AI response is converted into JSON and validated using Pydantic before being displayed.

This reduces the risk of unexpected response formats breaking the application.

---

🧪 Testing

The application should be tested using multiple realistic scenarios.

Test Case 1 — AI Internship

Input:

- Resume containing Python, AI, Streamlit and API projects.
- Job requiring Python, APIs, machine learning and Git.

Expected result:

- Relevant skills recognized.
- Missing requirements identified.
- Improvement suggestions generated.

Test Case 2 — Frontend Developer

Input:

- Resume focused on C++, Python and AI.
- Job requiring React, JavaScript, HTML and CSS.

Expected result:

- Frontend skill gaps identified.
- Resume mismatch clearly explained.

Test Case 3 — Backend Developer

Input:

- Resume containing Python and API projects.
- Job requiring Python, FastAPI, REST APIs and databases.

Expected result:

- Existing backend experience identified.
- Missing technologies highlighted.

Test Case 4 — Strong Resume Match

Input:

- Resume closely matching the job description.

Expected result:

- High ATS compatibility score.
- Relevant strengths identified.
- Fewer missing skills.

Test Case 5 — Weak Resume Match

Input:

- Resume with skills unrelated to the target position.

Expected result:

- Lower compatibility score.
- Important missing skills identified.
- Actionable recommendations provided.

---

🔒 Security

The project uses environment variables for API credentials.

The API key should never be hard-coded into "app.py" or committed to GitHub.



🎯 Learning Outcomes

This project demonstrates practical understanding of:

- Prompt engineering
- LLM API integration
- Structured AI outputs
- Pydantic data validation
- PDF processing
- Streamlit application development
- Environment variable management
- Error handling
- AI-powered application design
- Testing AI applications

---

🔮 Future Improvements

With additional development time, the application could be extended with:

- 📄 DOCX resume support
- 🧠 RAG-based job and career knowledge retrieval
- 📈 Skill-match visualization
- 🎯 Job-specific resume rewriting
- 🔗 LinkedIn profile analysis
- 📊 Resume comparison between multiple versions
- 💾 User history and saved analyses
- 🔐 User authentication
- ☁️ Cloud deployment
- 🤖 Automated job-description analysis
- 📧 Automated email/report generation

---

💼 Why This Project Matters

This project demonstrates how an LLM can be integrated into a real-world workflow rather than being used only as a basic chatbot.

It combines:

Problem → User Input → AI Processing → Structured Data → Useful Decision Support

The project was designed as a compact full-stack AI application suitable for demonstrating practical skills during technical interviews.

---

👩‍💻 Author

Ezza Saeed

BS Software Engineering Student

live:
https://aipowered-resume-analyzer-l9wdhyu27cnxpfpajmyevt.streamlit.app/