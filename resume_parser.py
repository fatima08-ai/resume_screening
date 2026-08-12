import re
import PyPDF2
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

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

def _extract_column_aware(pdf_file) -> str:
    """Reconstruct correct reading order from a PDF that may use side-by-side
    two-column tables (common in resumes, e.g. Education | Certifications).
    Works in a continuous document-wide coordinate space so a table can span
    a page break, and locks a column boundary from the cleanest split line
    in a block so narrow/lopsided rows still get classified correctly."""
    all_words = []
    y_offset = 0
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            for w in page.extract_words():
                all_words.append({
                    "text": w["text"], "x0": w["x0"], "x1": w["x1"],
                    "doctop": w["top"] + y_offset,
                })
            y_offset += page.height

    if not all_words:
        return ""

    all_words.sort(key=lambda w: (w["doctop"], w["x0"]))
    lines, current_line, current_top = [], [], None
    for w in all_words:
        if current_top is None or abs(w["doctop"] - current_top) <= 3:
            current_line.append(w)
            current_top = w["doctop"] if current_top is None else current_top
        else:
            lines.append(current_line)
            current_line = [w]
            current_top = w["doctop"]
    if current_line:
        lines.append(current_line)
    for line in lines:
        line.sort(key=lambda w: w["x0"])

    GAP_THRESHOLD = 15

    def line_gap_split(line):
        max_gap, split_idx = 0, None
        for i in range(len(line) - 1):
            gap = line[i + 1]["x0"] - line[i]["x1"]
            if gap > max_gap:
                max_gap, split_idx = gap, i + 1
        if max_gap > GAP_THRESHOLD:
            return split_idx, (line[split_idx - 1]["x1"] + line[split_idx]["x0"]) / 2
        return None, None

    output_lines = []
    i, n = 0, len(lines)
    while i < n:
        split_idx, split_x = line_gap_split(lines[i])
        if split_idx is None:
            output_lines.append(" ".join(w["text"] for w in lines[i]))
            i += 1
            continue

        boundary = split_x
        left_texts, right_texts = [], []
        j = i
        while j < n:
            s_idx, s_x = line_gap_split(lines[j])
            if s_idx is not None:
                left_texts.append(" ".join(w["text"] for w in lines[j][:s_idx]))
                right_texts.append(" ".join(w["text"] for w in lines[j][s_idx:]))
                boundary = s_x
                j += 1
                continue
            xs = [w["x0"] for w in lines[j]]
            if max(xs) < boundary:
                left_texts.append(" ".join(w["text"] for w in lines[j]))
                j += 1
            elif min(xs) > boundary:
                right_texts.append(" ".join(w["text"] for w in lines[j]))
                j += 1
            else:
                break
        output_lines.extend(left_texts)
        output_lines.extend(right_texts)
        i = j

    return "\n".join(output_lines)


def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from a PDF. Tries column-aware pdfplumber extraction
    first (correctly reconstructs multi-column resume layouts, which
    PyPDF2 often scrambles), falling back to plain PyPDF2 if pdfplumber
    fails or isn't installed."""
    if HAS_PDFPLUMBER:
        try:
            if hasattr(pdf_file, "seek"):
                pdf_file.seek(0)
            text = _extract_column_aware(pdf_file)
            if text.strip():
                return text
        except Exception as e:
            print(f"pdfplumber column-aware extraction failed, falling back to PyPDF2: {e}")

    text = ""
    try:
        if hasattr(pdf_file, "seek"):
            pdf_file.seek(0)
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
SECTION_ALIASES = {
    "experience": [
        "professional experience", "experience", "work experience", "employment history",
        "career history", "relevant experience", "employment", "work history", "career experience",
    ],
    "education": [
        "education", "academic background", "academic qualifications", "education & training",
    ],
    "certifications": [
        "certifications", "certification", "licenses & certifications",
        "certificates", "professional certifications", "credentials", "licenses",
    ],
    "projects": [
        "projects", "key projects", "notable projects", "selected projects",
        "personal projects", "side projects", "portfolio", "technical projects",
        "open source contributions",
    ],
}
ALL_HEADER_VARIANTS = [alias for aliases in SECTION_ALIASES.values() for alias in aliases]


def extract_section(text: str, section_key: str) -> list:
    aliases = SECTION_ALIASES[section_key]
    lines = text.split("\n")
    section_lines = []
    in_section = False

    for line in lines:
        stripped = line.strip()
        stripped_lower = stripped.lower()

        if stripped_lower in aliases:
            in_section = True
            continue

        if in_section and stripped_lower in ALL_HEADER_VARIANTS:
            break

        if in_section and stripped:
            if stripped.startswith("- ") or stripped.startswith("• "):
                section_lines.append(stripped[2:])
            else:
                if section_lines:
                    section_lines[-1] = section_lines[-1] + " " + stripped
                else:
                    section_lines.append(stripped)

    return section_lines
def split_merged_headers(text: str) -> str:
    """Some PDFs (especially two-column resumes) merge adjacent section
    headers onto one line, e.g. 'EDUCATION CERTIFICATIONS'. If a line is
    made up entirely of two or more known headers stuck together, split it
    back into separate lines so each header is detected correctly."""
    aliases_by_length = sorted(ALL_HEADER_VARIANTS, key=len, reverse=True)
    new_lines = []

    for line in text.split("\n"):
        remaining = line.strip().lower()
        matched = []
        while remaining:
            hit = next((a for a in aliases_by_length if remaining.startswith(a)), None)
            if not hit:
                matched = []
                break
            matched.append(hit)
            remaining = remaining[len(hit):].strip()

        if len(matched) >= 2:
            new_lines.extend(matched)
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def extract_all_sections(text: str) -> dict:
    text = split_merged_headers(text)
    return {
        "experience": extract_section(text, "experience"),
        "education": extract_section(text, "education"),
        "certifications": extract_section(text, "certifications"),
        "projects": extract_section(text, "projects"),
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