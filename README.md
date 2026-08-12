# AI-Powered Resume Screening — Recruiter Dashboard

A persistent, recruiter-facing resume screening tool that parses resumes, ranks candidates against a job description using AI-powered relevance scoring, and gives recruiters everything they need to act on the results — status tracking, private notes, AI-generated interview questions, AI-drafted emails, and a downloadable hiring report.

Originally built as Task 2 for the ML & AI Internship at Teerop Pvt Ltd, then rebuilt into this portfolio version with persistent sessions, a full custom theme system, and genuine AI-driven scoring in place of simple keyword counting.

## Features

**Sessions & persistence**
- Every job posting is a saved session (SQLite-backed) — start a new one or reload any past one
- Dashboard view summarizing every session at a glance (candidate counts, top score, status breakdown)
- Delete any session (with a confirmation step) to clean up test data
- Sessions are isolated per local installation — see [Limitations](#limitations) below

**Resume parsing**
- Multi-PDF upload with per-file error handling
- Column-aware PDF extraction that correctly reconstructs reading order for two-column resume layouts (a common source of scrambled text in naive PDF parsers), with automatic fallback to standard extraction if needed
- Extracts contact info, skills, education, experience, certifications, and projects, recognizing common header variants (e.g. "Key Projects," "Academic Background," "Certificates") rather than requiring exact wording

**AI-powered candidate scoring**
- Skills, Experience, Certifications, and Projects are each scored by sending the job description and the candidate's actual content to Groq (Llama 3.1) for a genuine relevance judgment — not just keyword counting
- Every AI-scored category has a safe fallback to a deterministic method (keyword matching / TF-IDF similarity) if the API call fails, so scoring never breaks
- Education uses a transparent, explainable degree-tier system
- Final score is a weighted combination: Skills 35%, Experience 30%, Education 15%, Certifications 10%, Projects 10%

**Recruiter workflow tools**
- Candidate status tracking (New / Shortlisted / Interview / Rejected)
- Private, timestamped notes per candidate
- AI-generated interview questions tailored to each candidate's matched/missing skills
- AI-drafted emails (rejection, interview invite, or under-review) based on current status
- Downloadable PDF hiring report summarizing the full session
- Rankings exportable to Excel with auto-fit column widths

**Interface**
- AI HR chatbot (Groq-powered) for natural-language questions about the candidate pool, with conversational memory and quick-question shortcuts
- Sortable/filterable rankings table, grouped bar chart score comparison, side-by-side two-candidate comparison view
- Full custom light/dark theme with a toggle, defaulting to light mode

## Tech Stack

| Component        | Technology                                  |
|-------------------|----------------------------------------------|
| Frontend          | Streamlit                                   |
| Database          | SQLite                                      |
| PDF Parsing       | pdfplumber (column-aware) with PyPDF2 fallback |
| PDF Report Generation | fpdf2                                   |
| AI Scoring & Chatbot | Groq API (Llama 3.1)                     |
| Fallback ML       | scikit-learn (TF-IDF, cosine similarity)    |
| Data Handling     | pandas, openpyxl                            |
| Visualizations    | Plotly                                      |

## Project Structure

```
resume_screening_portfolio/
├── app.py                 # Main Streamlit application
├── db.py                  # SQLite layer: sessions, candidates, statuses, notes
├── resume_parser.py       # Column-aware PDF parsing & info extraction
├── ranking_engine.py      # AI-powered + rule-based scoring
├── vector_store.py        # TF-IDF fallback similarity
├── chatbot.py             # Groq API integration
├── ui.py                  # Theme system (light/dark CSS)
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
cd resume_screening
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key

Sign up for free at [console.groq.com](https://console.groq.com) and create an API key. Create a file at `.streamlit/secrets.toml` in the project root:

```toml
GROQ_API_KEY = "your-key-here"
```

This file is gitignored and never committed. Without a key, the app still runs — AI-scored categories and the chatbot automatically fall back to non-AI methods.

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Usage

1. Start a new session: enter a job title, paste or upload a job description, upload candidate resumes as PDF.
2. Click **Process & Rank Candidates**.
3. Explore the tabs:
   - **Rankings** — sortable/filterable table, score comparison chart, Excel export
   - **Candidates** — full profile per candidate, status updates, private notes, AI interview questions, AI email drafts
   - **AI Chatbot** — ask natural-language questions about the candidate pool
   - **Compare** — side-by-side comparison of any two candidates
   - **Report** — generate and download a PDF hiring report
4. Switch to **Dashboard (all sessions)** in the sidebar for an overview of every job posting you've screened.

## Scoring Methodology

Each candidate's overall score is a weighted combination of five sub-scores. Skills, Experience, Certifications, and Projects are scored by an AI relevance judgment against the specific job description (falling back to keyword/TF-IDF matching if the API is unavailable); Education uses a fixed, explainable degree tier. This mix was a deliberate choice — AI judgment where nuance genuinely matters (is this candidate's certification relevant to *this* role), and a transparent rule where a simple, explainable answer is good enough (degree level).

## Limitations

These weights and heuristics are intentionally simple and explainable rather than opaque, so every ranking decision the system makes can be traced back to a specific, human-readable reason.

## Known Design Decisions

- **Education/Certification/Project scoring uses rule-based heuristics rather than deep NLP.** This was a deliberate choice for transparency and explainability — an HR user can understand exactly why a candidate scored the way they did, rather than trusting a black-box model.
- **TF-IDF similarity scores are intentionally modest even for strong matches.** This is expected cosine-similarity behavior across full documents, not a bug — it's one signal among five, not the sole determinant of ranking.

## Author

Fatima Jawad — ML & AI Internship, Teerop Pvt Ltd
=======
- **Session isolation is per-installation, not per-user or per-browser.** Each local copy of this app tracks its own sessions independently, using a local ID file rather than login. If multiple people run the app from the same cloned folder on a shared computer, they'll see each other's sessions; separate clones (or separate machines) stay fully isolated. This is a deliberate scope decision for a no-login local tool — proper multi-user isolation on a shared hosted deployment would require a real authentication system.
- **Scanned/image-only PDFs aren't supported** — parsing requires an actual text layer; OCR is out of scope for this version.
- **Highly unconventional resume layouts** (three-plus columns, heavy sidebar designs) may not parse cleanly. Standard single-column and common two-column layouts are well supported.
