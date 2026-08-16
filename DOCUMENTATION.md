# Implementation Report

**Project:** AI-Powered Resume Screening — Recruiter Dashboard (Portfolio Edition)

**Author:** Fatima Jawad

**Base:** Originally built as Task 2 for the ML & AI Internship, Teerop Pvt Ltd — extended into a full recruiter-facing tool with persistence, AI-driven scoring, and a custom UI system.

---

## How I approached it

The internship submission already had working core logic (parsing, ranking, chatbot), so this phase was about turning it into something a recruiter could actually use day-to-day: sessions that persist, a workflow around each candidate (status, notes, interview prep), and scoring that reflects real judgment instead of just keyword counting. I worked iteratively — get one piece solid, verify it against real data, move to the next — rather than redesigning everything at once.

---

## Architecture

| Layer | Lives in | Responsibility |
|---|---|---|
| Persistence | `db.py` | SQLite: sessions, candidates, statuses, notes |
| Input | `app.py` (sidebar) | Session management, resume/JD upload |
| Processing | `resume_parser.py` | PDF → structured candidate data |
| Analysis | `vector_store.py`, `ranking_engine.py` | Structured data → weighted scores |
| Output | `app.py` (tabs) | Scores → table, charts, reports, chatbot |
| Presentation | `ui.py` | Theme system, light/dark CSS |

---

## Key decisions

**AI-powered scoring, with mandatory fallbacks.**
Certifications and Projects originally scored purely on *count* — three certifications scored the same 75% regardless of whether they were relevant to the role. I moved Skills, Experience, Certifications, and Projects to genuine AI relevance judgment via Groq, but every single one falls back to the original deterministic method (keyword matching / TF-IDF) if the API call fails for any reason. Scoring should never break just because a network call did.

**Education stayed rule-based on purpose.**
Degree level is one of the few things where a simple, explainable tier genuinely is the right amount of sophistication — no ambiguity in "PhD > Master's > Bachelor's," so no reason to spend an API call judging it.

**Session isolation without a login system.**
I wanted "Load a past session" to only show a person's own sessions, without building full authentication. After multiple failed attempts at browser-based detection (see bugs below), I settled on a local ID file — correctly scoped as *per-installation*, not per-user, and documented as a known limitation rather than oversold as something it isn't.

---

## Bugs I actually ran into

These are included because they were real, and every one of them changed the final code — not a polished retelling.

### 1. A resume-scoring category was structurally broken, not just wrong

Certifications and Projects scores were identical across every candidate regardless of actual relevance — 3 certs always scored 75%, no matter what those certs were. The formula was pure counting (`min(count * 25, 100)`), blind to content entirely.

**Fix:** Replaced with AI relevance scoring against the specific job description, with the count-based method kept as a safe fallback.

### 2. The most heavily-weighted score category was functionally the least influential

Experience is weighted 30% — the highest of any category — but was scored via raw TF-IDF cosine similarity between the full resume and job description text. That method structurally compresses into a tiny 0-20% range even for a perfect match, since it's comparing whole-document word overlap, not judging relevance. A category weighted highest was barely moving the final score at all.

**Fix:** Same AI-relevance approach as above, scoring the extracted experience section specifically rather than the whole raw resume.

### 3. Two-column resumes silently scrambled Education and Certifications together

Some resumes lay out Education and Certifications side-by-side as two visual columns. Standard PDF text extraction reads left-to-right, top-to-bottom, which interleaves unrelated content from both columns onto the same line — a degree entry and a certification entry would end up merged into one garbled string, and the section headers themselves sometimes merged into one line like "EDUCATION CERTIFICATIONS," which broke exact-match header detection entirely.

**Fix:** Built a column-aware extraction pass using word-level x-coordinates from `pdfplumber` — detects a genuine column boundary from the cleanest split row in a block, then buckets every subsequent line (even lopsided ones with content on only one side) by position rather than by an unreliable per-line gap. Falls back to standard extraction if this fails.

### 4. Section headers required exact wording

The parser only recognized "Projects" as a header — resumes titled it "Key Projects" and the whole section, and every score depending on it, came back empty.

**Fix:** Replaced exact-string matching with an alias list per section (multiple real-world header phrasings), plus a pass that splits any merged/combined header lines before section detection runs.

### 5. Chat history was wiping itself immediately after answering

The AI chatbot appeared completely unresponsive — it never seemed to answer. The actual cause: a leftover line resetting `chat_history` to empty was sitting unconditionally in the sidebar's render path rather than inside the one button click it was meant to respond to. Since the chatbot's own answer flow ends in `st.rerun()`, the sidebar re-executed on every turn and wiped the answer a fraction of a second after it was added.

**Fix:** Moved the reset to only fire on an actual "Load a different session" action, where wiping history is the correct behavior.

### 6. Browser-based session detection failed across three different approaches

Wanted "Load a past session" scoped to the browser using it, without a login system. Tried two different cookie libraries and a manual localStorage/redirect approach — all three failed the same way: writing data to the browser worked, but reading it back into Python didn't, consistently, across unrelated libraries. That pattern pointed to something structural in how Streamlit's custom-component sandboxing interacted with the local environment, not a bug in any one library.

**Fix:** Stepped back and matched the solution to the actual constraint — this only needed to run locally, not on a shared server — so a local ID file, written and read directly by Python with no browser round-trip involved, solved it reliably. Documented clearly as per-installation scope, not per-browser or per-user, since that's an honest limitation rather than a solved problem.

---

## How I tested

| Level | What I did |
|---|---|
| Real data | Tested parsing and scoring against actual generated resumes with real two-column layouts, not just synthetic examples |
| Fallback paths | Verified every AI-scored category falls back correctly with no API key present, confirmed it returns the same values as the original deterministic method |
| Cross-theme | Checked every UI component in both light and dark mode individually, since several (chat input, file upload pills, dropdowns) required devtools inspection to find the actual element being styled rather than assumed selectors |
| Session lifecycle | Created, loaded, and deleted sessions; confirmed delete removes candidates and notes with no orphaned rows |

---

## Beyond the internship submission

- Persistent SQLite-backed sessions with a full dashboard view across all job postings
- Candidate status tracking, private notes, AI-generated interview questions, AI-drafted emails
- Downloadable PDF hiring report and Excel export with auto-fit columns
- AI-powered relevance scoring in place of keyword/count-based scoring, with safe fallbacks throughout
- Column-aware PDF parsing for two-column resume layouts
- Full custom light/dark theme system built from scratch