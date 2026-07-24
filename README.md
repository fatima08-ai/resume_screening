# AI-Powered Resume Screening & Candidate Ranking System

An intelligent HR assistant that automatically parses resumes, matches them against a job description, and ranks candidates using a weighted, multi-factor scoring system — with an AI chatbot for natural-language candidate Q&A.

Built as Task 2 for the ML & AI Internship at Teerop Pvt Ltd.

## Features

- **Multi-PDF resume upload** with per-file processing and error handling
- **Automatic information extraction**: name, email, phone, skills (78+ recognized technologies across 6 categories), education, experience, certifications, and projects
- **Job description input** — paste as text or upload as PDF
- **5-category weighted candidate ranking**: Skills (35%), Experience (30%), Education (15%), Certifications (10%), Projects (10%)
- **TF-IDF + cosine similarity** for semantic experience matching
- **AI HR chatbot** powered by Groq (Llama 3.1 8B Instant) — ask natural-language questions about candidates, with conversational memory
- **Interactive rankings table** — sortable, filterable by minimum score, color-coded (green ≥80%, yellow 60–79%, red <60%), exportable to CSV
- **Grouped bar chart** comparing all candidates across every scoring category
- **Radar chart** for a visual 5-category profile of any selected candidate
- **Side-by-side candidate comparison tab** — pick any two candidates, compare scores metric-by-metric with directional indicators, and see shared vs. unique skills
- **Skill coverage progress bar** per candidate, showing matched vs. required skills for the given JD
- **Sample CV generator** for quick testing without real resumes

## Tech Stack

| Component        | Technology                              |
|-------------------|------------------------------------------|
| Frontend          | Streamlit                               |
| PDF Generation    | fpdf2                                   |
| PDF Parsing       | PyPDF2                                  |
| ML/NLP            | scikit-learn (TF-IDF, cosine similarity) |
| AI Chatbot        | Groq API (Llama 3.1 8B Instant)         |
| Data Handling     | pandas, NumPy                           |
| Visualizations    | Plotly                                  |

No PyTorch, FAISS, or GPU requirements — lightweight and cross-platform.

## Project Structure

```
resume_screening/
├── app.py                 # Main Streamlit application
├── cv_generator.py        # Sample CV creation module
├── resume_parser.py       # PDF parsing & info extraction
├── ranking_engine.py      # Scoring & ranking algorithms
├── vector_store.py        # TF-IDF vectorization & similarity
├── chatbot.py             # Groq API integration
├── requirements.txt       # Python dependencies
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/fatima08-ai/resume_screening.git
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

### 4. Get a Groq API key

Sign up for free at [console.groq.com](https://console.groq.com), create an API key, and keep it handy — you'll enter it directly in the app's sidebar. It is never stored or hardcoded anywhere in this project.

### 5. Run the app

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

## Usage

1. Enter your Groq API key in the sidebar.
2. Click **Generate Sample CVs** to create test resumes, or upload your own PDF resumes.
3. Review or edit the job description (a default AI/ML Engineer JD is pre-filled), or upload a JD as PDF.
4. Click **Process & Rank Candidates**.
5. Explore the four tabs:
   - **Rankings** — sortable/filterable table, grouped bar chart, radar chart
   - **Candidates** — full profile per candidate, including skill coverage
   - **AI Chatbot** — ask questions about the candidates
   - **Compare** — side-by-side comparison of any two candidates

## Scoring Methodology

Each candidate's overall score is a weighted combination of five sub-scores:

- **Skills (35%)** — percentage of JD-required skills the candidate has, matched against a 78-skill database spanning Programming, Web, AI/ML, Cloud, Databases, and Tools.
- **Experience (30%)** — TF-IDF vectorization + cosine similarity between the full resume text and the job description, capturing overall contextual relevance beyond just keyword matching.
- **Education (15%)** — a transparent heuristic based on the highest degree level detected (PhD > Master's > Bachelor's > other/unrecognized).
- **Certifications (10%)** — scaled by number of certifications listed, capped at 100%.
- **Projects (10%)** — scaled by number of relevant projects listed, capped at 100%.

These weights and heuristics are intentionally simple and explainable rather than opaque, so every ranking decision the system makes can be traced back to a specific, human-readable reason.

## Known Design Decisions

- **Education/Certification/Project scoring uses rule-based heuristics rather than deep NLP.** This was a deliberate choice for transparency and explainability — an HR user can understand exactly why a candidate scored the way they did, rather than trusting a black-box model.
- **TF-IDF similarity scores are intentionally modest even for strong matches.** This is expected cosine-similarity behavior across full documents, not a bug — it's one signal among five, not the sole determinant of ranking.

## Author

Fatima Jawad — ML & AI Internship, Teerop Pvt Ltd
