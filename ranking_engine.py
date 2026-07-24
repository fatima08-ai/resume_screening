from vector_store import compute_similarity_scores

WEIGHTS = {
    "skills": 0.35,
    "experience": 0.30,
    "education": 0.15,
    "certifications": 0.10,
    "projects": 0.10,
}


def extract_required_skills(job_description: str, all_skills: list) -> list:
    
    jd_lower = job_description.lower()
    required = [skill for skill in all_skills if skill in jd_lower]
    return required


def score_skill_match(candidate_skills: list, required_skills: list) -> float:
    if not required_skills:
        return 0.0

    candidate_set = set(candidate_skills)
    required_set = set(required_skills)
    matched = candidate_set.intersection(required_set)

    return round((len(matched) / len(required_set)) * 100, 1)
def score_experience_match(candidate_resume_text: str, job_description: str) -> float:
    
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


def score_certifications_match(certifications_list: list) -> float:
    
    count = len(certifications_list)
    return min(count * 25.0, 100.0)


def score_projects_match(projects_list: list) -> float:
    
    count = len(projects_list)
    return min(count * 33.0, 100.0)
def calculate_overall_score(candidate: dict, job_description: str, all_skills: list) -> dict:
   
    required_skills = extract_required_skills(job_description, all_skills)

    skill_score = score_skill_match(candidate["skills"], required_skills)
    experience_score = score_experience_match(candidate["raw_text"], job_description)
    education_score = score_education_match(candidate["education"])
    cert_score = score_certifications_match(candidate["certifications"])
    project_score = score_projects_match(candidate["projects"])

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


def rank_candidates(candidates: list, job_description: str, all_skills: list) -> list:
   
    scored = [
        calculate_overall_score(c, job_description, all_skills) for c in candidates
    ]
    scored.sort(key=lambda x: x["overall"], reverse=True)
    return scored