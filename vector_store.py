from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_similarity_scores(resume_texts: list, job_description: str) -> list:
    
    if not resume_texts or not job_description.strip():
        return [0.0] * len(resume_texts)

    documents = [job_description] + resume_texts

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    jd_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(jd_vector, resume_vectors)[0]

    scores = [round(float(sim) * 100, 1) for sim in similarities]
    return scores
