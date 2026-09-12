import io
import pytest
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from app.core.security import create_access_token, get_password_hash
from app.models.enums import UserRole
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.services.resume_parser import ResumeParserService
from app.services.skill_extractor import SkillExtractionService
from app.services.skill_normalizer import SkillNormalizationService


def make_test_pdf(lines: list[str]) -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)

    font = DictionaryObject()
    font[NameObject("/Type")] = NameObject("/Font")
    font[NameObject("/Subtype")] = NameObject("/Type1")
    font[NameObject("/BaseFont")] = NameObject("/Helvetica")

    fonts = DictionaryObject()
    fonts[NameObject("/F1")] = font

    resources = DictionaryObject()
    resources[NameObject("/Font")] = fonts
    page[NameObject("/Resources")] = resources

    content_ops = ["BT /F1 12 Tf 14 TL 72 720 Td"]
    for line in lines:
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_ops.append(f"({escaped}) Tj T*")
    content_ops.append("ET")
    content_str = "\n".join(content_ops)

    stream = DecodedStreamObject()
    stream.set_data(content_str.encode("latin1"))
    page[NameObject("/Contents")] = stream

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


@pytest.fixture
def auth_student(db_session):
    user = User(
        email="resume_student@skillmatch.edu",
        hashed_password=get_password_hash("StudentPass123!"),
        full_name="Original Name",
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = StudentProfile(
        user_id=user.id,
        college="Original University",
        degree="B.S. / B.Sc.",
        branch="General Science",
        gpa=3.2,
        summary="Original summary",
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)

    token = create_access_token(user.id)
    return user, profile, token


def test_skill_normalization_aliases():
    # Prompt specific required normalization pairs:
    assert SkillNormalizationService.normalize("ML") == "Machine Learning"
    assert SkillNormalizationService.normalize("machine learning") == "Machine Learning"
    assert SkillNormalizationService.normalize("machine-learning") == "Machine Learning"
    assert SkillNormalizationService.normalize("JS") == "JavaScript"
    assert SkillNormalizationService.normalize("javascript") == "JavaScript"
    assert SkillNormalizationService.normalize("ReactJS") == "React"
    assert SkillNormalizationService.normalize("react.js") == "React"
    assert SkillNormalizationService.normalize("Postgres") == "PostgreSQL"
    assert SkillNormalizationService.normalize("postgresql") == "PostgreSQL"

    # Additional standard tech abbreviations:
    assert SkillNormalizationService.normalize("k8s") == "Kubernetes"
    assert SkillNormalizationService.normalize("ts") == "TypeScript"
    assert SkillNormalizationService.normalize("cpp") == "C++"
    assert SkillNormalizationService.normalize("c#") == "C#"
    assert SkillNormalizationService.normalize("py") == "Python"
    assert SkillNormalizationService.normalize("aws") == "AWS"
    assert SkillNormalizationService.normalize("ci/cd") == "CI/CD"


def test_skill_normalization_deduplication():
    raw_list = [
        "ML",
        "Machine Learning",
        "machine-learning",
        "ReactJS",
        "react.js",
        "React",
        "JS",
        "javascript",
        "Postgres",
        "PostgreSQL",
    ]
    normalized = SkillNormalizationService.normalize_list(raw_list)
    assert normalized == ["Machine Learning", "React", "JavaScript", "PostgreSQL"]


def test_canonical_skills_in_database(db_session, auth_student):
    user, profile, _ = auth_student

    # Create canonical skill
    s1 = SkillNormalizationService.get_or_create_canonical_skill(db_session, "ML")
    assert s1.name == "Machine Learning"
    assert s1.normalized_name == "machine learning"

    # Call with variation
    s2 = SkillNormalizationService.get_or_create_canonical_skill(db_session, "machine-learning")
    assert s1.id == s2.id

    # Attach to student
    st_skill1, is_new1 = SkillNormalizationService.add_skill_to_student(
        db_session, profile.id, "ML", proficiency="Beginner"
    )
    assert is_new1 is True

    # Attempt to attach alias again
    st_skill2, is_new2 = SkillNormalizationService.add_skill_to_student(
        db_session, profile.id, "machine learning", proficiency="Advanced"
    )
    assert is_new2 is False
    assert st_skill1.id == st_skill2.id
    assert st_skill2.proficiency == "Advanced"


def test_skill_extraction_service():
    sample_text = """
    Software Engineer with hands-on experience in ML and deep learning.
    Built full-stack services using Python, FastAPI, ReactJS, and Postgres.
    Deployed containerized microservices to AWS utilizing Docker and k8s.
    Strong background in Data Structures & Algorithms and REST APIs.
    """
    extracted = SkillExtractionService.extract_skills_from_text(sample_text)
    assert "Machine Learning" in extracted
    assert "Deep Learning" in extracted
    assert "Python" in extracted
    assert "FastAPI" in extracted
    assert "React" in extracted
    assert "PostgreSQL" in extracted
    assert "AWS" in extracted
    assert "Docker" in extracted
    assert "Kubernetes" in extracted
    assert "Data Structures & Algorithms" in extracted
    assert "REST APIs" in extracted


def test_resume_upload_non_destructive(client, auth_student, db_session):
    user, profile, token = auth_student

    pdf_bytes = make_test_pdf([
        "Alex Morgan",
        "alex.morgan@university.edu | (555) 019-2834",
        "EDUCATION",
        "National Institute of Technology",
        "Bachelor of Technology in Computer Science, GPA: 3.82",
        "Expected Graduation: 2027",
        "SKILLS",
        "Python, ML, PyTorch, ReactJS, Postgres, Docker, Git",
        "PROJECTS",
        "NeuralClassifier - Distributed Inference",
        "Engineered an automated benchmarking suite for deep neural networks.",
        "CERTIFICATIONS",
        "Deep Learning Specialization by DeepLearning.AI | 2025",
    ])

    files = {"file": ("alex_morgan_resume.pdf", pdf_bytes, "application/pdf")}
    res = client.post("/api/resume/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    ext = data["extracted_data"]
    assert ext["name"] == "Alex Morgan"
    assert ext["email"] == "alex.morgan@university.edu"
    assert "National Institute of Technology" in ext["college"]
    assert ext["degree"] == "B.Tech / B.E."
    assert ext["branch"] == "Computer Science"
    assert ext["gpa"] == 3.82
    assert "Machine Learning" in ext["skills"]
    assert "React" in ext["skills"]
    assert "PostgreSQL" in ext["skills"]

    # CRITICAL: Verify student profile in database was NOT modified
    db_session.refresh(user)
    db_session.refresh(profile)
    assert user.full_name == "Original Name"
    assert profile.college == "Original University"
    assert profile.gpa == 3.2


def test_resume_confirm_updates_profile(client, auth_student, db_session):
    user, profile, token = auth_student
    headers = {"Authorization": f"Bearer {token}"}

    confirm_payload = {
        "name": "Alex Morgan Verified",
        "college": "National Institute of Technology",
        "degree": "B.Tech / B.E.",
        "branch": "Computer Science",
        "gpa": 3.85,
        "summary": "Undergraduate CS student passionate about machine learning systems.",
        "skills": ["Python", "ML", "ReactJS", "Postgres", "Docker"],
        "projects": [
            {
                "title": "NeuralClassifier",
                "description": "Benchmark quantization engine.",
                "technologies": ["Python", "PyTorch"],
            }
        ],
        "certifications": [
            {
                "name": "Deep Learning Specialization",
                "issuing_organization": "DeepLearning.AI",
                "issue_date": "2025",
            }
        ],
    }

    res = client.post("/api/resume/confirm", json=confirm_payload, headers=headers)
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["success"] is True
    assert res_data["skills_added"] >= 4
    assert res_data["projects_added"] == 1
    assert res_data["certifications_added"] == 1

    # Verify DB state
    db_session.refresh(user)
    db_session.refresh(profile)
    assert user.full_name == "Alex Morgan Verified"
    assert profile.college == "National Institute of Technology"
    assert profile.degree == "B.Tech / B.E."
    assert profile.gpa == 3.85
    assert profile.summary == "Undergraduate CS student passionate about machine learning systems."

    # Verify normalized skills attached to student
    student_skills = [ss.skill.name for ss in profile.skills]
    assert "Machine Learning" in student_skills
    assert "React" in student_skills
    assert "PostgreSQL" in student_skills

    # Calling confirm again with same skills does not duplicate
    res2 = client.post(
        "/api/resume/confirm",
        json={"skills": ["ML", "machine-learning", "Machine Learning"]},
        headers=headers,
    )
    assert res2.status_code == 200
    assert res2.json()["skills_added"] == 0  # No duplicates added!


def test_resume_upload_multiple_structures(client):
    # Structure 1: Industry Senior Engineer
    pdf_senior = make_test_pdf([
        "Sarah Connor",
        "sarah.connor@cyberdyne.io",
        "WORK EXPERIENCE",
        "Senior Systems Architect at CloudScale | 2024 - Present",
        "Architected distributed Kubernetes clusters handling 50k requests per second.",
        "TECHNICAL SKILLS",
        "Go, Kubernetes, AWS, Terraform, Docker, CI/CD, Linux",
        "CERTIFICATIONS",
        "AWS Solutions Architect Professional | 2024",
    ])
    res1 = client.post(
        "/api/resume/upload",
        files={"file": ("sarah_senior.pdf", pdf_senior, "application/pdf")},
    )
    assert res1.status_code == 200
    ext1 = res1.json()["extracted_data"]
    assert ext1["name"] == "Sarah Connor"
    assert "Kubernetes" in ext1["skills"]
    assert "AWS" in ext1["skills"]
    assert "CI/CD" in ext1["skills"]

    # Structure 2: Minimalist Research Resume
    pdf_minimal = make_test_pdf([
        "David Hilbert",
        "hilbert@math.harvard.edu",
        "Harvard University - Master of Science in Mathematics",
        "SKILLS",
        "Python, PyTorch, Linear Algebra, Machine Learning",
    ])
    res2 = client.post(
        "/api/resume/upload",
        files={"file": ("david_minimal.pdf", pdf_minimal, "application/pdf")},
    )
    assert res2.status_code == 200
    ext2 = res2.json()["extracted_data"]
    assert ext2["name"] == "David Hilbert"
    assert "Harvard" in ext2["college"]
    assert "PyTorch" in ext2["skills"]
    assert "Machine Learning" in ext2["skills"]


def test_resume_upload_invalid_file(client):
    # Non-PDF
    res = client.post(
        "/api/resume/upload",
        files={"file": ("resume.txt", b"plain text", "text/plain")},
    )
    assert res.status_code == 400
    assert "PDF" in res.json()["detail"]

    # Empty PDF
    res_empty = client.post(
        "/api/resume/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert res_empty.status_code == 400
