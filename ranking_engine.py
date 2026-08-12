import json
from groq import Groq

from vector_store import compute_similarity_scores

WEIGHTS = {
    "skills": 0.35,
    "experience": 0.30,
    "education": 0.15,
    "certifications": 0.10,
    "projects": 0.10,
}


def _call_groq_relevance_score(item_type: str, items_text: str, job_description: str, api_key: str):
    """Ask Groq to rate how relevant a candidate's certifications/projects are
    to the job description, on a 0-100 scale. Returns None on any failure
    (missing key, API error, bad JSON) so the caller can fall back to the
    count-based score instead of breaking ranking entirely."""
    if not api_key or not items_text.strip():
        return None

    try:
        client = Groq(api_key=api_key)
        system_prompt = (
            f"You are a strict technical recruiter scoring how relevant a candidate's "
            f"{item_type} are to a specific job posting. "
            "Reply with ONLY a JSON object, no other text, no markdown fences: "
            '{"score": <integer 0-100>, "reason": "<one short sentence>"}. '
            "Score based on genuine relevance to the job, not just quantity — "
            "irrelevant items should score low even if there are several of them."
        )
        user_prompt = (
            f"Job description:\n{job_description}\n\n"
            f"Candidate's {item_type}:\n{items_text}\n\n"
            "Rate relevance 0-100."
        )
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        score = float(data["score"])
        return max(0.0, min(100.0, score))
    except Exception as e:
        print(f"AI relevance scoring failed for {item_type}, falling back to count-based: {e}")
        return None


def extract_required_skills(job_description: str, all_skills: list) -> list:
    
    jd_lower = job_description.lower()
    required = [skill for skill in all_skills if skill in jd_lower]
    return required


def score_skill_match(candidate_skills: list, required_skills: list, job_description: str = "", api_key: str = "") -> float:
    if job_description and candidate_skills:
        items_text = "\n".join(f"- {s}" for s in candidate_skills)
        ai_score = _call_groq_relevance_score("technical skills", items_text, job_description, api_key)
        if ai_score is not None:
            return round(ai_score, 1)

    if not required_skills:
        return 0.0

    candidate_set = set(candidate_skills)
    required_set = set(required_skills)
    matched = candidate_set.intersection(required_set)

    return round((len(matched) / len(required_set)) * 100, 1)
def score_experience_match(candidate_resume_text: str, job_description: str, experience_list: list = None, api_key: str = "") -> float:
    if experience_list:
        items_text = "\n".join(f"- {e}" for e in experience_list)
        ai_score = _call_groq_relevance_score("professional experience", items_text, job_description, api_key)
        if ai_score is not None:
            return round(ai_score, 1)

    scores = compute_similarity_scores([candidate_resume_text], job_description)
    return scores[0]


def score_education_match(education_list: list) -> float:
    
    if not education_list:
        return 0.0

    education_text = " ".join(education_list).lower()

    if "phd" in education_text or "ph.d" in education_text or "doctorate" in education_text:
        return 100.0
    elif "m.s." in education_text or "master" in education_text or "m.tech" in education_text:
        return 85.0
    elif "b.s." in education_text or "bachelor" in education_text or "b.tech" in education_text:
        return 60.0
    else:
        return 30.0 


def score_certifications_match(certifications_list: list, job_description: str = "", api_key: str = "") -> float:
    if not certifications_list:
        return 0.0

    items_text = "\n".join(f"- {c}" for c in certifications_list)
    ai_score = _call_groq_relevance_score("certifications", items_text, job_description, api_key)
    if ai_score is not None:
        return round(ai_score, 1)

    count = len(certifications_list)
    return min(count * 25.0, 100.0)


def score_projects_match(projects_list: list, job_description: str = "", api_key: str = "") -> float:
    if not projects_list:
        return 0.0

    items_text = "\n".join(f"- {p}" for p in projects_list)
    ai_score = _call_groq_relevance_score("projects", items_text, job_description, api_key)
    if ai_score is not None:
        return round(ai_score, 1)

    count = len(projects_list)
    return min(count * 33.0, 100.0)
def calculate_overall_score(candidate: dict, job_description: str, all_skills: list, api_key: str = "") -> dict:
   
    required_skills = extract_required_skills(job_description, all_skills)

    skill_score = score_skill_match(candidate["skills"], required_skills, job_description, api_key)
    experience_score = score_experience_match(candidate["raw_text"], job_description, candidate.get("experience"), api_key)
    education_score = score_education_match(candidate["education"])
    cert_score = score_certifications_match(candidate["certifications"], job_description, api_key)
    project_score = score_projects_match(candidate["projects"], job_description, api_key)

    overall = (
        skill_score * WEIGHTS["skills"]
        + experience_score * WEIGHTS["experience"]
        + education_score * WEIGHTS["education"]
        + cert_score * WEIGHTS["certifications"]
        + project_score * WEIGHTS["projects"]
    )

    return {
        "name": candidate["name"],
        "email": candidate["email"],
        "overall": round(overall, 1),
        "skills": skill_score,
        "experience": experience_score,
        "education": education_score,
        "certifications": cert_score,
        "projects": project_score,
        "matched_skills": list(set(candidate["skills"]).intersection(set(required_skills))),
        "missing_skills": list(set(required_skills) - set(candidate["skills"])),
        "education_details": candidate["education"],
        "experience_details": candidate["experience"],
        "certifications_details": candidate["certifications"],
        "projects_details": candidate["projects"],
        "all_skills": candidate["skills"],
    }


def rank_candidates(candidates: list, job_description: str, all_skills: list, api_key: str = "") -> list:
   
    scored = [
        calculate_overall_score(c, job_description, all_skills, api_key) for c in candidates
    ]
    scored.sort(key=lambda x: x["overall"], reverse=True)
    return scored