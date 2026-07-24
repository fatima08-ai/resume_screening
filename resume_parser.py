import re
import PyPDF2

SKILL_CATEGORIES = {
    "Programming": [
        "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
        "rust", "kotlin", "swift", "php", "scala",
    ],
    "Web": [
        "react", "angular", "vue.js", "node.js", "django", "flask", "fastapi",
        "next.js", "express.js", "html", "css", "graphql", "tailwind", "bootstrap",
        "webpack",
    ],
    "AI/ML": [
        "tensorflow", "pytorch", "scikit-learn", "langchain", "nlp",
        "computer vision", "deep learning", "machine learning", "transformers", "rag",
        "keras", "opencv", "pandas", "numpy", "hugging face", "llm", "spacy",
    ],
    "Cloud": [
        "aws", "azure", "gcp", "docker", "kubernetes", "mlops", "terraform",
        "serverless", "lambda", "cloudformation",
    ],
    "Databases": [
        "sql", "postgresql", "mongodb", "redis", "mysql", "sqlite", "elasticsearch",
        "dynamodb", "cassandra",
    ],
    "Tools": [
        "git", "jenkins", "ci/cd", "agile", "scrum", "tableau", "jwt", "oauth",
        "microservices", "rest api", "linux", "bash", "jira", "figma", "postman",
    ],
}

ALL_SKILLS = [skill for category in SKILL_CATEGORIES.values() for skill in category]

def extract_text_from_pdf(pdf_file) -> str:
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
    return text
def extract_contact_info(text: str) -> dict:

    contact = {"name": "Unknown", "email": "Not found", "phone": "Not found"}

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if lines:
        contact["name"] = lines[0]

    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    if email_match:
        contact["email"] = email_match.group()

    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,7}", text)
    if phone_match:
        contact["phone"] = phone_match.group().strip()

    return contact
def extract_skills(text: str) -> list:
    text_lower = text.lower()
    found_skills = []

    for skill in ALL_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return found_skills
def extract_section(text: str, section_name: str, next_sections: list) -> list:
    
    lines = text.split("\n")
    section_lines = []
    in_section = False

    for line in lines:
        stripped = line.strip()

        if stripped.lower() == section_name.lower():
            in_section = True
            continue

        if in_section and stripped.lower() in [s.lower() for s in next_sections]:
            break

        if in_section and stripped:
            if stripped.startswith("- "):
                section_lines.append(stripped[2:])
            else:
                if section_lines:
                    section_lines[-1] = section_lines[-1] + " " + stripped
                else:
                    section_lines.append(stripped)

    return section_lines
def extract_all_sections(text: str) -> dict:
    
    headers = ["Skills", "Professional Experience", "Education", "Certifications", "Projects"]

    return {
        "experience": extract_section(text, "Professional Experience", headers),
        "education": extract_section(text, "Education", headers),
        "certifications": extract_section(text, "Certifications", headers),
        "projects": extract_section(text, "Projects", headers),
    }
def parse_resume(pdf_file, filename: str = "") -> dict:
    text = extract_text_from_pdf(pdf_file)

    if not text.strip():
        return {
            "filename": filename,
            "name": "Unknown",
            "email": "Not found",
            "phone": "Not found",
            "skills": [],
            "education": [],
            "experience": [],
            "certifications": [],
            "projects": [],
            "raw_text": "",
        }

    contact = extract_contact_info(text)
    skills = extract_skills(text)
    sections = extract_all_sections(text)

    return {
        "filename": filename,
        "name": contact["name"],
        "email": contact["email"],
        "phone": contact["phone"],
        "skills": skills,
        "education": sections["education"],
        "experience": sections["experience"],
        "certifications": sections["certifications"],
        "projects": sections["projects"],
        "raw_text": text,
    }
if __name__ == "__main__":
    import os

    for filename in os.listdir("sample_cvs"):
        path = os.path.join("sample_cvs", filename)
        result = parse_resume(path, filename)
        print(f"\n{'='*50}")
        print(f"File: {filename}")
        print(f"Name: {result['name']}")
        print(f"Email: {result['email']}")
        print(f"Skills ({len(result['skills'])}): {result['skills']}")
