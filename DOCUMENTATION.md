# Implementation Report

**Project:** AI-Powered Resume Screening & Candidate Ranking System

**Author:** Fatima Jawad

**Internship:** ML & AI Internship, Teerop Pvt Ltd — Task 2

---

## How I approached it

Instead of writing the whole app in one go, I broke it into six modules and built them one at a time — testing each one on its own before connecting it to anything else.

| Order | Module | What it does |
|---|---|---|
| 1 | `cv_generator.py` | Generates sample resumes, so I'd have consistent test data from day one |
| 2 | `resume_parser.py` | Pulls structured info out of a resume PDF |
| 3 | `vector_store.py` | TF-IDF + cosine similarity for text matching |
| 4 | `ranking_engine.py` | Combines everything into the 5-category weighted score |
| 5 | `chatbot.py` | Groq API integration |
| 6 | `app.py` | The Streamlit app that ties it all together |

Building it this way meant that by the time I got to the UI, I already trusted the underlying logic. Anything that broke after that point was almost always a UI/integration issue, not a scoring or parsing bug — which made debugging a lot faster.

---

## Architecture

Roughly four layers, each one only depending on the layer before it.

| Layer | Lives in | Responsibility |
|---|---|---|
| Input | `app.py` (sidebar) | Resume uploads, JD input, API key |
| Processing | `resume_parser.py` | Raw PDF → structured candidate data |
| Analysis | `vector_store.py`, `ranking_engine.py` | Structured data → weighted scores |
| Output | `app.py` (tabs) | Scores → table, charts, profiles, chatbot |

---

## Bugs I actually ran into

I'm including these because I think they're more useful than pretending the build went perfectly. All four were real, and all four changed something in the final code.

### 1. A skill silently missing from detection

While testing skill extraction, one sample candidate came back with 15 skills instead of the expected 16.

Turned out "Tableau" never made it into the skill list when I expanded it from ~40 to 78 entries — nothing was wrong with the matching logic, the word just wasn't in the dictionary it was checking against.

**Fix:** Added it under the "Tools" category and recounted to confirm.

This one stuck with me because it didn't throw an error anywhere — it just quietly produced a slightly wrong number. Made me more careful about checking output against known values instead of just watching for crashes.

### 2. PDF line-wrapping split single bullet points in two

When a long bullet point wrapped onto a second line in the generated PDF, PyPDF2 read that as two separate lines with no memory of them being one sentence.

My parser was treating the second line as a brand new bullet, so a single degree entry was coming back as two broken fragments.

**Fix:** Check whether a line starts with the `"- "` bullet marker. If it doesn't, it's a continuation of the previous line, and it gets merged back on instead of starting a new entry.

### 3. Chat input box appearing in the wrong place

In the chatbot tab, the message box kept showing up above the latest question and answer instead of below it.

The cause was ordering — `st.chat_input()` was being called before the code that displayed the newest message, and inside a tab it doesn't automatically pin itself to the bottom the way it would on a plain page.

**Fix:** Append new messages straight to chat history and trigger `st.rerun()`, so the history loop (which runs before the input box) always renders the latest turn in the right order.

### 4. Comparison tab arrows drifting out of alignment

In the side-by-side comparison tab, the little arrows showing which candidate scored higher started drifting away from their matching row the further down the list you looked.

I'd created the three columns once, outside the loop, and reused them for all six categories — since the content in each column wasn't the same height every time, they gradually fell out of sync.

**Fix:** Create a fresh set of columns inside the loop, once per category, so every row is independent.

---

## A few decisions I made on purpose

**Education, certifications, and projects use simple rule-based scoring, not a heavier NLP model.**
I wanted every score to be explainable — if someone asks "why did this candidate get 85% on education," I can point to the exact rule. Given the brief also asked to avoid heavy dependencies, this felt like the right tradeoff.

**I didn't force the top score above 80%, even though the benchmark scenario in the brief suggested that.**
My top candidate landed at 75.2%. The ranking order was correct and clearly separated from the others (75.2% vs 51.2% vs 37.9%), and I could explain exactly why the number came out where it did — TF-IDF similarity across a full resume is naturally modest even for a strong match, since it's comparing overall word overlap, not just the standout lines. Tuning the weights just to hit a number felt less honest than leaving it as-is.

**I used three sample candidates instead of two**, so the rankings and comparison tab would have a bit more range to actually demonstrate against.

---

## How I tested

| Level | What I did |
|---|---|
| Per module | Ran each file on its own and checked printed output against values I already knew were correct |
| Full pipeline | Ran the complete app with all three sample candidates and checked the data all the way through, from upload to display |
| Clean environment | Reinstalled everything into a brand new virtual environment using only `requirements.txt`, to make sure nothing depended on something already sitting on my machine |
| Error paths | Deliberately tried to break it — no resumes uploaded, no job description, no API key — all gave a clear message instead of crashing |

---

## Beyond the base requirements

- Radar chart for a candidate's 5-category profile
- Side-by-side comparison tab with directional score indicators and shared/unique skill breakdown
- Skill coverage progress bar per candidate
- Sortable, filterable, color-coded rankings table with CSV export
- Custom dark theme for a more polished look overall