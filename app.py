import streamlit as st
import os

from cv_generator import generate_sample_cvs
from resume_parser import parse_resume, ALL_SKILLS
from ranking_engine import rank_candidates
from chatbot import get_chatbot_response

st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide",
)

st.markdown("""
<style>
    .stApp {
        background-color: #0f1117;
    }

    h1 {
        color: #ffffff;
        font-weight: 700;
    }

    section[data-testid="stSidebar"] {
        background-color: #161923;
        border-right: 1px solid #262b3d;
    }

    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #7c9eff;
        font-size: 1.05rem;
        margin-top: 1.2rem;
    }

    button[kind="primary"] {
        background-color: #7c9eff;
        color: #0f1117;
        font-weight: 600;
        border: none;
    }
    button[kind="primary"]:hover {
        background-color: #5c7fe0;
    }

    button[data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 500;
    }

    .streamlit-expanderHeader {
        background-color: #1a1d29;
        border-radius: 8px;
    }

    div[data-testid="stMetric"] {
        background-color: #1a1d29;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #262b3d;
    }
</style>
""", unsafe_allow_html=True)

if "rankings" not in st.session_state:
    st.session_state.rankings = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "candidates_processed" not in st.session_state:
    st.session_state.candidates_processed = False

with st.sidebar:
    st.header("🔑 Groq API Key")
    api_key = st.text_input(
        "Enter Groq API Key",
        type="password",
        help="Get a free key at console.groq.com",
    )

    st.header("📋 Sample Data")
    if st.button("Generate Sample CVs"):
        paths = generate_sample_cvs()
        st.success(f"Generated {len(paths)} sample CVs in 'sample_cvs/' folder!")

    st.header("📤 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload Resume PDFs",
        type=["pdf"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        st.info(f"{len(uploaded_files)} resume(s) uploaded")

    st.header("📝 Job Description")
    default_jd = """Senior AI/ML Engineer

Requirements: 5+ years Python and ML experience, TensorFlow/PyTorch, NLP, Computer Vision, AWS/GCP, Docker, Kubernetes, MLOps. Preferred: RAG systems, FastAPI, PostgreSQL, Team leadership."""

    job_description = st.text_area(
        "Paste Job Description",
        value=default_jd,
        height=200,
    )

    jd_pdf = st.file_uploader("Or upload JD as PDF", type=["pdf"], key="jd_pdf_uploader")

    process_clicked = st.button("🚀 Process & Rank Candidates", type="primary")
   
st.title("📄 AI-Powered Resume Screening & Candidate Ranking")
st.caption("Intelligent HR Assistant with Groq AI Chatbot")

if process_clicked:
    if not uploaded_files:
        st.error("Please upload at least one resume PDF before processing.")
    elif not job_description.strip() and not jd_pdf:
        st.error("Please provide a job description (text or PDF).")
    else:
        with st.spinner("Processing resumes..."):
            final_jd = job_description
            if jd_pdf is not None:
                from resume_parser import extract_text_from_pdf
                final_jd = extract_text_from_pdf(jd_pdf)

            candidates = []
            for file in uploaded_files:
                try:
                    result = parse_resume(file, filename=file.name)
                    candidates.append(result)
                except Exception as e:
                    st.warning(f"Could not process {file.name}: {e}")

            if candidates:
                rankings = rank_candidates(candidates, final_jd, ALL_SKILLS)
                st.session_state.rankings = rankings
                st.session_state.candidates_processed = True
                st.session_state.chat_history = []  
                st.success(f"Processed {len(candidates)} candidate(s) successfully!")
            else:
                st.error("No resumes could be processed. Please check your files.")


if not st.session_state.candidates_processed:
    st.info("👋 Upload resumes and provide a job description to get started!")
else:
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Rankings", "👤 Candidates", "💬 AI Chatbot", "⚖️ Compare"])

    with tab1:
        st.header("🏆 Candidate Rankings")

        rankings = st.session_state.rankings

        import pandas as pd

        df = pd.DataFrame([{
            "Rank": i,
            "Candidate": r["name"],
            "Overall": r["overall"],
            "Skills": r["skills"],
            "Experience": r["experience"],
            "Education": r["education"],
            "Certifications": r["certifications"],
            "Projects": r["projects"],
        } for i, r in enumerate(rankings, start=1)])

        min_score = st.slider("Filter: minimum overall score (%)", 0, 100, 0)
        filtered_df = df[df["Overall"] >= min_score]

        def highlight_score(val):
            if isinstance(val, (int, float)):
                if val >= 80:
                    return "background-color: #1e4d2b; color: white"
                elif val >= 60:
                    return "background-color: #5c4d1e; color: white"
                else:
                    return "background-color: #5c1e1e; color: white"
            return ""

        styled_df = filtered_df.style.map(highlight_score, subset=["Overall"])

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Rankings as CSV",
            data=csv_data,
            file_name="candidate_rankings.csv",
            mime="text/csv",
        )
        st.subheader("📊 Score Comparison")

        import plotly.graph_objects as go

        names = [r["name"] for r in rankings]
        categories = ["skills", "experience", "education", "certifications", "projects"]
        category_labels = ["Skills", "Experience", "Education", "Certifications", "Projects"]

        fig = go.Figure()
        for cat, label in zip(categories, category_labels):
            fig.add_trace(go.Bar(
                name=label,
                x=names,
                y=[r[cat] for r in rankings],
            ))

        fig.update_layout(
            barmode="group",
            yaxis_title="Score (%)",
            xaxis_title="Candidate",
            legend_title="Category",
            height=450,
        )

        st.plotly_chart(fig, use_container_width=True)
        st.subheader("🎯 Candidate Profile Radar")

        selected_candidate = st.selectbox(
            "Select a candidate to view their profile radar",
            options=names,
        )

        selected_data = next(r for r in rankings if r["name"] == selected_candidate)

        radar_categories = category_labels + [category_labels[0]]  # close the loop
        radar_values = [selected_data[cat] for cat in categories] + [selected_data[categories[0]]]

        radar_fig = go.Figure()
        radar_fig.add_trace(go.Scatterpolar(
            r=radar_values,
            theta=radar_categories,
            fill="toself",
            name=selected_candidate,
        ))

        radar_fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=450,
        )

        st.plotly_chart(radar_fig, use_container_width=True)
    with tab2:
        st.header("👤 Candidate Profiles")

        rankings = st.session_state.rankings

        for i, r in enumerate(rankings, start=1):
            with st.expander(f"{r['name']} — Score: {r['overall']}%"):
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("📧 Contact")
                    st.write(f"**Email:** {r['email']}")

                    st.subheader("💼 Skills")
                    st.write(", ".join(r["all_skills"]) if r["all_skills"] else "None listed")

                    st.subheader("🎓 Education")
                    for edu in r["education_details"]:
                        st.write(f"- {edu}")

                    st.subheader("🛠️ Experience")
                    for exp in r["experience_details"]:
                        st.write(f"- {exp}")

                with col2:
                    st.subheader("📜 Certifications")
                    for cert in r["certifications_details"]:
                        st.write(f"- {cert}")

                    st.subheader("🚀 Projects")
                    for proj in r["projects_details"]:
                        st.write(f"- {proj}")

                    st.subheader("✅ Matched Skills (for this JD)")
                    st.write(", ".join(r["matched_skills"]) if r["matched_skills"] else "None")

                    total_required = len(r["matched_skills"]) + len(r["missing_skills"])
                    if total_required > 0:
                        st.subheader("📈 Skill Coverage")
                        matched_pct = len(r["matched_skills"]) / total_required
                        st.progress(matched_pct, text=f"{len(r['matched_skills'])} of {total_required} required skills matched ({matched_pct*100:.0f}%)")
    with tab3:
        st.header("💬 AI HR Chatbot (Powered by Groq)")

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
                        question_to_ask,
                        st.session_state.rankings,
                        api_key,
                        st.session_state.chat_history[:-1],  # history *before* this question
                    )

                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()
    with tab4:
        st.header("⚖️ Side-by-Side Comparison")

        rankings = st.session_state.rankings
        candidate_names = [r["name"] for r in rankings]

        col1, col2 = st.columns(2)
        with col1:
            candidate_a_name = st.selectbox("Candidate A", candidate_names, index=0, key="compare_a")
        with col2:
            default_b = 1 if len(candidate_names) > 1 else 0
            candidate_b_name = st.selectbox("Candidate B", candidate_names, index=default_b, key="compare_b")

        candidate_a = next(r for r in rankings if r["name"] == candidate_a_name)
        candidate_b = next(r for r in rankings if r["name"] == candidate_b_name)

        st.subheader("📊 Score Comparison")

        compare_categories = ["overall", "skills", "experience", "education", "certifications", "projects"]
        compare_labels = ["Overall", "Skills", "Experience", "Education", "Certifications", "Projects"]

        for cat, label in zip(compare_categories, compare_labels):
            comp_col1, comp_col2, comp_col3 = st.columns([2, 1, 2])
            val_a = candidate_a[cat]
            val_b = candidate_b[cat]

            with comp_col1:
                st.metric(label=f"{candidate_a_name} — {label}", value=f"{val_a}%")
            with comp_col2:
                if val_a > val_b:
                    st.markdown("<h3 style='text-align: center;'>⬅️</h3>", unsafe_allow_html=True)
                elif val_b > val_a:
                    st.markdown("<h3 style='text-align: center;'>➡️</h3>", unsafe_allow_html=True)
                else:
                    st.markdown("<h3 style='text-align: center;'>➖</h3>", unsafe_allow_html=True)
            with comp_col3:
                st.metric(label=f"{candidate_b_name} — {label}", value=f"{val_b}%")

        st.divider()

        st.subheader("💼 Skills Comparison")
        skills_a = set(candidate_a["all_skills"])
        skills_b = set(candidate_b["all_skills"])

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.write(f"**Only {candidate_a_name} has:**")
            unique_a = skills_a - skills_b
            st.write(", ".join(unique_a) if unique_a else "None")
        with sc2:
            st.write("**Both have:**")
            shared = skills_a.intersection(skills_b)
            st.write(", ".join(shared) if shared else "None")
        with sc3:
            st.write(f"**Only {candidate_b_name} has:**")
            unique_b = skills_b - skills_a
            st.write(", ".join(unique_b) if unique_b else "None")