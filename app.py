"""
app.py — Portfolio Edition
----------------------------
AI-Powered Resume Screening & Candidate Ranking System
Recruiter-facing version with persistent sessions, candidate status
tracking, private notes, PDF hiring reports, AI interview questions,
and AI email drafts.
"""

import streamlit as st
import os
import json
import io
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF

from resume_parser import parse_resume, ALL_SKILLS, extract_text_from_pdf
from ranking_engine import rank_candidates
from chatbot import get_chatbot_response
from ui import apply_theme
from db import (
    init_db, create_session, get_all_sessions, get_session, delete_session,
    save_candidate, get_candidates_for_session, update_candidate_status,
    add_note, get_notes_for_candidate,
)
import uuid
from datetime import datetime, timedelta
import pathlib

def sanitize_pdf_text(text: str) -> str:
    """Replace characters the default PDF font can't render."""
    replacements = {"\u2014": "-", "\u2013": "-", "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2026": "..."}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

st.set_page_config(
    page_title="AI Resume Screening — Recruiter Dashboard",
    page_icon=":material/description:",
    layout="wide",
)

init_db()
apply_theme()

BROWSER_ID_FILE = pathlib.Path(__file__).parent / ".browser_id.txt"

if BROWSER_ID_FILE.exists():
    browser_id = BROWSER_ID_FILE.read_text().strip()
else:
    browser_id = str(uuid.uuid4())
    BROWSER_ID_FILE.write_text(browser_id)

if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

STATUS_OPTIONS = ["New", "Shortlisted", "Interview", "Rejected"]

with st.sidebar:
    st.title(":material/description: Resume Screening")

    existing_sessions = get_all_sessions(browser_id)

    view_mode = st.radio("View", ["Screen Candidates", "Dashboard (all sessions)"])
    st.divider()

    if view_mode == "Screen Candidates":
        if existing_sessions:
            mode = st.radio("What would you like to do?", ["Start a new session", "Load a past session"])
        else:
            mode = "Start a new session"
            st.caption("No past sessions yet — start your first one below.")

        st.divider()

        if mode == "Start a new session":
            job_title = st.text_input("Job Title", placeholder="e.g. Senior AI/ML Engineer")
            job_description = st.text_area("Job Description", placeholder="Paste the job description here...", height=180)
            jd_pdf = st.file_uploader("Or upload JD as PDF", type=["pdf"], key="jd_pdf_uploader")

            st.subheader(":material/upload_file: Upload Resumes")
            uploaded_files = st.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

            st.divider()
            api_key = st.secrets.get("GROQ_API_KEY", "")
            process_clicked = st.button("Process & Rank Candidates", icon=":material/rocket_launch:", type="primary")
        else:
            session_options = {f"{s['job_title']} — {s['created_at'][:10]}": s['id'] for s in existing_sessions}
            selected_label = st.selectbox("Select a session", list(session_options.keys()))
            selected_session_id = session_options[selected_label]

            if st.button("Load Session", icon=":material/folder_open:", type="primary"):
                st.session_state.active_session_id = selected_session_id
            confirm_key = f"confirm_delete_{selected_session_id}"
            if st.session_state.get(confirm_key):
                st.warning(f"Delete '{selected_label}' and all its candidates? This can't be undone.")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Yes, delete it", icon=":material/delete_forever:", type="primary"):
                        delete_session(selected_session_id)
                        st.session_state[confirm_key] = False
                        if st.session_state.active_session_id == selected_session_id:
                            st.session_state.active_session_id = None
                        st.rerun()
                with col_no:
                    if st.button("Cancel"):
                        st.session_state[confirm_key] = False
                        st.rerun()
            else:
                if st.button("Delete Session", icon=":material/delete:"):
                    st.session_state[confirm_key] = True
                    st.rerun()
                    st.session_state.chat_history = []

            api_key = st.secrets.get("GROQ_API_KEY", "")
            process_clicked = False
    else:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        process_clicked = False

if view_mode == "Screen Candidates" and process_clicked:
    if not uploaded_files:
        st.error("Please upload at least one resume PDF before processing.")
    elif not job_description.strip() and not jd_pdf:
        st.error("Please provide a job description (text or PDF).")
    elif not job_title.strip():
        st.error("Please enter a job title.")
    else:
        with st.spinner("Processing resumes..."):
            final_jd = job_description
            if jd_pdf is not None:
                final_jd = extract_text_from_pdf(jd_pdf)

            candidates = []
            for file in uploaded_files:
                try:
                    result = parse_resume(file, filename=file.name)
                    candidates.append(result)
                except Exception as e:
                    st.warning(f"Could not process {file.name}: {e}")

            if candidates:
                rankings = rank_candidates(candidates, final_jd, ALL_SKILLS, api_key)
                sid = create_session(job_title, final_jd, browser_id)
                for r in rankings:
                    save_candidate(sid, r)

                st.session_state.active_session_id = sid
                st.session_state.chat_history = []
                st.success(f"Processed {len(candidates)} candidate(s) and saved session '{job_title}'!")
                st.rerun()
            else:
                st.error("No resumes could be processed. Please check your files.")

if view_mode == "Dashboard (all sessions)":
    st.title(":material/dashboard: Recruiter Dashboard")
    st.caption("All job postings and screening activity")

    if not existing_sessions:
        st.info("No sessions yet. Switch to 'Screen Candidates' to start your first one.")
    else:
        dash_rows = []
        for s in existing_sessions:
            candidates = get_candidates_for_session(s["id"])
            shortlisted = sum(1 for c in candidates if c["status"] == "Shortlisted")
            interview = sum(1 for c in candidates if c["status"] == "Interview")
            rejected = sum(1 for c in candidates if c["status"] == "Rejected")
            top_score = max([c["overall_score"] for c in candidates], default=0)

            dash_rows.append({
                "Job Title": s["job_title"],
                "Created": s["created_at"][:10],
                "Candidates": len(candidates),
                "Top Score": f"{top_score}%",
                "Shortlisted": shortlisted,
                "Interview": interview,
                "Rejected": rejected,
            })

        st.table(pd.DataFrame(dash_rows).style.hide(axis="index"))

if view_mode == "Screen Candidates":
    st.title(":material/description: AI-Powered Resume Screening & Candidate Ranking")
    st.caption("Recruiter dashboard, powered by Groq AI")

    if not st.session_state.active_session_id:
        st.info("Start a new session or load a past one from the sidebar to get started!", icon=":material/waving_hand:")
    else:
        session = get_session(st.session_state.active_session_id)
        db_candidates = get_candidates_for_session(st.session_state.active_session_id)

        if not db_candidates:
            st.warning("This session has no candidates.")
        else:
            rankings = [c["data"] for c in db_candidates]
            db_by_name = {c["name"]: c for c in db_candidates}

            st.subheader(f"Job: {session['job_title']}")

            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                ":material/emoji_events: Rankings",
                ":material/person: Candidates",
                ":material/chat: AI Chatbot",
                ":material/balance: Compare",
                ":material/summarize: Report",
            ])

            with tab1:
                st.header(":material/emoji_events: Candidate Rankings")

                df = pd.DataFrame([{
                    "Rank": i,
                    "Candidate": r["name"],
                    "Overall": r["overall"],
                    "Skills": r["skills"],
                    "Experience": r["experience"],
                    "Education": r["education"],
                    "Certifications": r["certifications"],
                    "Projects": r["projects"],
                    "Status": db_by_name[r["name"]]["status"],
                } for i, r in enumerate(rankings, start=1)])

                min_score = st.slider("Filter: minimum overall score (%)", 0, 100, 0)
                filtered_df = df[df["Overall"] >= min_score]

                def highlight_score(val):
                    is_dark = st.session_state.get("theme", "Dark") == "Dark"
                    if isinstance(val, (int, float)):
                        if val >= 80:
                            bg, fg = ("#1e4d2b", "white") if is_dark else ("#c6e6cf", "#1c1c1a")
                        elif val >= 60:
                            bg, fg = ("#5c4d1e", "white") if is_dark else ("#f0dfa8", "#1c1c1a")
                        else:
                            bg, fg = ("#5c1e1e", "white") if is_dark else ("#f2c6c6", "#1c1c1a")
                        return f"background-color: {bg}; color: {fg}"
                    return ""

                styled_df = filtered_df.style.format({
                    "Overall": "{:.1f}%", "Skills": "{:.1f}%", "Experience": "{:.1f}%",
                    "Education": "{:.1f}%", "Certifications": "{:.1f}%", "Projects": "{:.1f}%",
                }).map(highlight_score, subset=["Overall"]).hide(axis="index")
                st.table(styled_df)

                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name="Rankings")
                    worksheet = writer.sheets["Rankings"]
                    for col_idx, col_name in enumerate(filtered_df.columns, start=1):
                        max_len = max(
                            filtered_df[col_name].astype(str).map(len).max(),
                            len(col_name),
                        ) + 2
                        worksheet.column_dimensions[worksheet.cell(row=1, column=col_idx).column_letter].width = max_len

                st.download_button("Download Rankings as Excel", data=excel_buffer.getvalue(),
                                    file_name="candidate_rankings.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    icon=":material/download:")

                st.subheader(":material/bar_chart: Score Comparison")
                names = [r["name"] for r in rankings]
                categories = ["skills", "experience", "education", "certifications", "projects"]
                category_labels = ["Skills", "Experience", "Education", "Certifications", "Projects"]

                fig = go.Figure()
                for cat, label in zip(categories, category_labels):
                    fig.add_trace(go.Bar(name=label, x=names, y=[r[cat] for r in rankings]))

                is_dark = st.session_state.get("theme", "Dark") == "Dark"
                text_color = "#eceef2" if is_dark else "#1c1c1a"
                grid_color = "#2a2e3a" if is_dark else "#dcdad3"
                fig.update_layout(
                    barmode="group", height=450,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=text_color),
                    legend=dict(title="Category", font=dict(color=text_color)),
                    xaxis=dict(title=dict(text="Candidate", font=dict(color=text_color)),
                               tickfont=dict(color=text_color), gridcolor=grid_color, linecolor=grid_color),
                    yaxis=dict(title=dict(text="Score (%)", font=dict(color=text_color)),
                               tickfont=dict(color=text_color), gridcolor=grid_color, linecolor=grid_color),
                )
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.header(":material/person: Candidate Profiles")

                for r in rankings:
                    db_row = db_by_name[r["name"]]
                    expand_key = f"expanded_{db_row['id']}"
                    if expand_key not in st.session_state:
                        st.session_state[expand_key] = False

                    with st.expander(f"{r['name']} - Score: {r['overall']}% | Status: {db_row['status']}", expanded=st.session_state[expand_key]):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader(":material/mail: Contact")
                            st.write(f"**Email:** {r['email']}")

                            st.subheader(":material/work: Skills")
                            st.write(", ".join(r["all_skills"]) if r["all_skills"] else "None listed")

                            st.subheader(":material/school: Education")
                            for edu in r["education_details"]:
                                st.write(f"- {edu}")

                            st.subheader(":material/engineering: Experience")
                            for exp in r["experience_details"]:
                                st.write(f"- {exp}")

                        with col2:
                            st.subheader(":material/verified: Certifications")
                            for cert in r["certifications_details"]:
                                st.write(f"- {cert}")

                            st.subheader(":material/rocket_launch: Projects")
                            for proj in r["projects_details"]:
                                st.write(f"- {proj}")

                        st.divider()

                        st.subheader(":material/label: Status")
                        current_status = db_row["status"]
                        new_status = st.selectbox(
                            "Update status", STATUS_OPTIONS,
                            index=STATUS_OPTIONS.index(current_status),
                            key=f"status_{db_row['id']}",
                        )
                        if new_status != current_status:
                            update_candidate_status(db_row["id"], new_status)
                            st.session_state[expand_key] = True
                            st.success(f"Status updated to {new_status}")
                            st.rerun()

                        st.subheader(":material/edit_note: Private Notes")
                        new_note = st.text_area("Add a note", key=f"note_input_{db_row['id']}", height=80)
                        if st.button("Save Note", icon=":material/save:", key=f"note_btn_{db_row['id']}"):
                            if new_note.strip():
                                add_note(db_row["id"], new_note.strip())
                                st.session_state[expand_key] = True
                                st.success("Note saved.")
                                st.rerun()

                        existing_notes = get_notes_for_candidate(db_row["id"])
                        for n in existing_notes:
                            st.caption(f"{n['created_at'][:16]} — {n['note_text']}")

                        st.divider()

                        st.subheader(":material/mic: AI Interview Questions")
                        if st.button("Generate Interview Questions", icon=":material/auto_awesome:", key=f"iq_{db_row['id']}"):
                            if not api_key:
                                st.warning("Enter your Groq API key in the sidebar first.")
                            else:
                                with st.spinner("Generating questions..."):
                                    prompt = (
                                        f"Generate 5 targeted interview questions for {r['name']}, "
                                        f"based on their matched skills ({', '.join(r['matched_skills']) or 'none'}) "
                                        f"and missing skills ({', '.join(r['missing_skills']) or 'none'}) "
                                        f"relative to this role. Focus on probing their strengths and "
                                        f"clarifying their gaps."
                                    )
                                    answer = get_chatbot_response(prompt, rankings, api_key, [])
                                    st.write(answer)

                        st.subheader(":material/mail: AI Email Draft")
                        if st.button("Draft Email", icon=":material/edit:", key=f"email_{db_row['id']}"):
                            if not api_key:
                                st.warning("Enter your Groq API key in the sidebar first.")
                            else:
                                with st.spinner("Drafting email..."):
                                    if current_status == "Rejected":
                                        prompt = f"Write a brief, kind, professional rejection email to {r['name']} for this role."
                                    elif current_status in ("Shortlisted", "Interview"):
                                        prompt = f"Write a brief, warm, professional email to {r['name']} inviting them to interview for this role."
                                    else:
                                        prompt = f"Write a brief, professional email to {r['name']} acknowledging their application is under review."
                                    answer = get_chatbot_response(prompt, rankings, api_key, [])
                                    st.write(answer)

            with tab3:
                st.header(":material/chat: AI HR Chatbot (Powered by Groq)")

                if not api_key:
                    st.warning("Please enter your Groq API key in the sidebar to use the chatbot.")
                else:
                    st.success("Chatbot ready! Ask questions about the candidates.")

                    st.write("**Quick Questions:**")
                    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
                    quick_question = None
                    with qcol1:
                        if st.button("Who is the best candidate?"):
                            quick_question = "Who is the best candidate and why?"
                    with qcol2:
                        if st.button("Compare the candidates"):
                            quick_question = "Compare all the candidates in detail."
                    with qcol3:
                        if st.button("Who has more experience?"):
                            quick_question = "Which candidate has the most relevant experience?"
                    with qcol4:
                        if st.button("Recommend the top candidate"):
                            quick_question = "Give a final recommendation on who to hire."

                    for msg in st.session_state.chat_history:
                        with st.chat_message(msg["role"]):
                            st.write(msg["content"])

                    user_input = st.chat_input("Ask a question about the candidates...")
                    question_to_ask = quick_question or user_input

                    if question_to_ask:
                        st.session_state.chat_history.append({"role": "user", "content": question_to_ask})
                        with st.spinner("Thinking..."):
                            answer = get_chatbot_response(
                                question_to_ask, rankings, api_key,
                                st.session_state.chat_history[:-1],
                            )
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                        st.rerun()

            with tab4:
                st.header(":material/balance: Side-by-Side Comparison")

                candidate_names = [r["name"] for r in rankings]
                col1, col2 = st.columns(2)
                with col1:
                    candidate_a_name = st.selectbox("Candidate A", candidate_names, index=0, key="compare_a")
                with col2:
                    default_b = 1 if len(candidate_names) > 1 else 0
                    candidate_b_name = st.selectbox("Candidate B", candidate_names, index=default_b, key="compare_b")

                candidate_a = next(r for r in rankings if r["name"] == candidate_a_name)
                candidate_b = next(r for r in rankings if r["name"] == candidate_b_name)

                st.subheader(":material/bar_chart: Score Comparison")
                compare_categories = ["overall", "skills", "experience", "education", "certifications", "projects"]
                compare_labels = ["Overall", "Skills", "Experience", "Education", "Certifications", "Projects"]

                for cat, label in zip(compare_categories, compare_labels):
                    comp_col1, comp_col2, comp_col3 = st.columns([2, 1, 2])
                    val_a, val_b = candidate_a[cat], candidate_b[cat]
                    with comp_col1:
                        st.metric(label=f"{candidate_a_name} — {label}", value=f"{val_a}%")
                    with comp_col2:
                        if val_a > val_b:
                            arrow = "←"
                        elif val_b > val_a:
                            arrow = "→"
                        else:
                            arrow = "−"
                        st.markdown(f"<div style='text-align: center; padding-top: 14px; font-size: 22px;'>{arrow}</div>", unsafe_allow_html=True)
                    with comp_col3:
                        st.metric(label=f"{candidate_b_name} — {label}", value=f"{val_b}%")

                st.divider()
                st.subheader(":material/work: Skills Comparison")
                skills_a, skills_b = set(candidate_a["all_skills"]), set(candidate_b["all_skills"])
                sc1, sc2, sc3 = st.columns(3)
                with sc1:
                    st.write(f"**Only {candidate_a_name} has:**")
                    st.write(", ".join(skills_a - skills_b) or "None")
                with sc2:
                    st.write("**Both have:**")
                    st.write(", ".join(skills_a & skills_b) or "None")
                with sc3:
                    st.write(f"**Only {candidate_b_name} has:**")
                    st.write(", ".join(skills_b - skills_a) or "None")

            with tab5:
                st.header(":material/summarize: Downloadable Hiring Report")
                st.caption("A formatted PDF summary of this session's rankings, ready to share with a hiring manager.")

                if st.button("Generate PDF Report", icon=":material/picture_as_pdf:", type="primary"):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica", "B", 18)
                    pdf.cell(0, 12, "Candidate Ranking Report", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", "", 11)
                    pdf.cell(0, 8, f"Job: {session['job_title']}", new_x="LMARGIN", new_y="NEXT")
                    pdf.cell(0, 8, f"Generated: {session['created_at'][:10]}", new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(6)

                    for i, r in enumerate(rankings, start=1):
                        db_row = db_by_name[r["name"]]
                        pdf.set_font("Helvetica", "B", 13)
                        pdf.set_x(pdf.l_margin)
                        pdf.cell(0, 8, sanitize_pdf_text(f"{i}. {r['name']} - {r['overall']}% ({db_row['status']})"), new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", "", 10)

                        pdf.set_x(pdf.l_margin)
                        pdf.multi_cell(0, 6,
                            f"Skills: {r['skills']}%  Experience: {r['experience']}%  "
                            f"Education: {r['education']}%  Certs: {r['certifications']}%  Projects: {r['projects']}%")

                        pdf.set_x(pdf.l_margin)
                        pdf.multi_cell(0, 6, f"Matched skills: {', '.join(r['matched_skills']) or 'None'}")

                        pdf.set_x(pdf.l_margin)
                        pdf.multi_cell(0, 6, f"Missing skills: {', '.join(r['missing_skills']) or 'None'}")
                        pdf.ln(4)

                    pdf_bytes = bytes(pdf.output())
                    st.download_button(
                        "Download Report PDF",
                        data=pdf_bytes,
                        file_name=f"hiring_report_{session['job_title'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        icon=":material/download:",
                    )