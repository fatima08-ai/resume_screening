from fpdf import FPDF
import os

SAMPLE_CANDIDATES = [
    {
        "name": "John Anderson",
        "email": "john.anderson@email.com",
        "phone": "+1-555-0147",
        "education": [
            "M.S. in Computer Science, Stanford University, 2016 - 2018, GPA: 3.9/4.0",
            "B.S. in Computer Science, UC San Diego, 2012 - 2016, GPA: 3.7/4.0",
        ],
        "experience": [
            "Senior Machine Learning Engineer, DeepVision AI (2021 - Present): "
            "Led development of computer vision pipelines using PyTorch and TensorFlow, "
            "deployed models on AWS with Docker and Kubernetes.",
            "ML Engineer, DataForge Inc. (2018 - 2021): "
            "Built NLP models for document classification, worked with LangChain and "
            "scikit-learn, mentored junior engineers.",
        ],
        "skills": [
            "Python", "TensorFlow", "PyTorch", "Scikit-learn", "LangChain", "NLP",
            "Computer Vision", "Deep Learning", "AWS", "GCP", "Docker", "Kubernetes",
            "MLOps", "FastAPI", "PostgreSQL", "Git", "RAG", "Transformers",
        ],
        "certifications": [
            "AWS Certified Machine Learning - Specialty",
            "TensorFlow Developer Certificate",
            "Deep Learning Specialization (Coursera)",
            "Kubernetes Certified Application Developer",
        ],
        "projects": [
            "Built a RAG-based internal knowledge assistant reducing support ticket "
            "resolution time by 40 percent.",
            "Designed an MLOps pipeline for automated model retraining and deployment.",
            "Published a computer vision model for defect detection in manufacturing.",
        ],
    },
    {
        "name": "Sarah Williams",
        "email": "sarah.williams@email.com",
        "phone": "N/A",
        "education": [
            "B.S. in Computer Science, University of California, Berkeley, "
            "2014 - 2018, GPA: 3.7/4.0",
        ],
        "experience": [
            "Full Stack Developer, WebCraft Solutions (2019 - Present): "
            "Built and maintained React and Node.js applications, integrated "
            "REST APIs, managed MongoDB and PostgreSQL databases.",
            "Junior Developer, StartupHub (2018 - 2019): "
            "Developed features for a Django-based e-commerce platform.",
        ],
        "skills": [
            "JavaScript", "React", "Node.js", "Next.js", "Express.js", "Django",
            "MongoDB", "PostgreSQL", "Docker", "Git", "CI/CD", "GraphQL", "HTML",
            "CSS", "Agile", "Scrum", "JWT", "OAuth", "Microservices", "Jenkins",
        ],
        "certifications": [
            "AWS Certified Solutions Architect - Associate",
            "Docker Certified Associate",
            "MongoDB Associate Developer",
            "Certified Scrum Master",
        ],
        "projects": [
            "Led migration of a monolithic app to a microservices architecture.",
            "Built a real-time chat feature using WebSockets and Node.js.",
            "Implemented CI/CD pipelines cutting deployment time by 60 percent.",
        ],
    },
    {
        "name": "Fatima Jawad",
        "email": "fatima.jawad@email.com",
        "phone": "+92-300-1234567",
        "education": [
            "M.S. in Data Science, University of Edinburgh, 2019 - 2021, GPA: 3.8/4.0",
            "B.S. in Computer Engineering, National University of Sciences and Technology (NUST), "
            "2015 - 2019, GPA: 3.7/4.0",
        ],
        "experience": [
            "Data Scientist, FinTech Analytics (2021 - Present): "
            "Built ML pipelines for fraud detection using Python, scikit-learn, "
            "and deployed models with FastAPI on GCP.",
            "Data Analyst Intern, RetailMetrics (2020 - 2020): "
            "Performed exploratory data analysis and built dashboards.",
        ],
        "skills": [
            "Python", "Scikit-learn", "Pandas", "NumPy", "SQL", "PostgreSQL",
            "FastAPI", "GCP", "Docker", "NLP", "Computer Vision", "Git",
            "TensorFlow", "Machine Learning", "Deep Learning", "Tableau",
        ],
        "certifications": [
            "Google Professional Data Engineer",
            "Deep Learning Specialization (Coursera)",
        ],
        "projects": [
            "Developed a fraud detection model improving precision by 25 percent.",
            "Built an automated data quality monitoring dashboard.",
        ],
    },
]
class ResumeCVPdf(FPDF):

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 30, 30)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(180, 180, 180)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(3)

    def body_text(self, text):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6, text)
        self.ln(1)
    
def generate_cv_pdf(candidate: dict, output_path: str) -> str:
    pdf = ResumeCVPdf()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 10, candidate["name"], new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(90, 90, 90)
    contact_line = f"Email: {candidate['email']}    Phone: {candidate['phone']}"
    pdf.cell(0, 7, contact_line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.section_title("Skills")
    pdf.body_text(", ".join(candidate["skills"]))

    pdf.section_title("Professional Experience")
    for exp in candidate["experience"]:
        pdf.body_text("- " + exp)

    pdf.section_title("Education")
    for edu in candidate["education"]:
        pdf.body_text("- " + edu)

    pdf.section_title("Certifications")
    for cert in candidate["certifications"]:
        pdf.body_text("- " + cert)

    pdf.section_title("Projects")
    for proj in candidate["projects"]:
        pdf.body_text("- " + proj)

    pdf.output(output_path)
    return output_path
def generate_sample_cvs(output_dir: str = "sample_cvs") -> list:
    
    os.makedirs(output_dir, exist_ok=True)
    generated_paths = []

    for candidate in SAMPLE_CANDIDATES:
        filename = "cv_" + candidate["name"].lower().replace(" ", "_") + ".pdf"
        path = os.path.join(output_dir, filename)
        generate_cv_pdf(candidate, path)
        generated_paths.append(path)

    return generated_paths


if __name__ == "__main__":
    paths = generate_sample_cvs()
    print(f"Generated {len(paths)} sample CVs:")
    for p in paths:
        print(f"  - {p}")