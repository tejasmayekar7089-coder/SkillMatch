import io
import re
from typing import Any, Dict, List, Optional, Tuple
import pypdf
from app.services.skill_extractor import SkillExtractionService
from app.services.skill_normalizer import SkillNormalizationService


class ResumeParserService:
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """Extracts UTF-8 text from a PDF byte stream using pypdf."""
        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n".join(text_parts).strip()
        except Exception as e:
            raise ValueError(f"Failed to parse PDF document: {str(e)}")

    @classmethod
    def parse_resume_text(cls, text: str) -> Dict[str, Any]:
        """
        Parses unstructured resume text into structured fields:
        name, email, phone, college, degree, branch, gpa, academic_year,
        graduation_year, skills, projects, experience, certifications, summary.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        email = cls._extract_email(text)
        phone = cls._extract_phone(text)
        name = cls._extract_name(lines, email)
        college = cls._extract_college(text)
        degree = cls._extract_degree(text)
        branch = cls._extract_branch(text)
        gpa = cls._extract_gpa(text)
        academic_year, grad_year = cls._extract_academic_years(text)
        skills = SkillExtractionService.extract_skills_from_text(text)
        projects = cls._extract_projects(text)
        experience = cls._extract_experience(text)
        certifications = cls._extract_certifications(text)
        summary = cls._extract_summary(text, lines)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "college": college,
            "degree": degree,
            "branch": branch,
            "gpa": gpa,
            "academic_year": academic_year,
            "graduation_year": grad_year,
            "summary": summary,
            "skills": skills,
            "projects": projects,
            "experience": experience,
            "certifications": certifications,
        }

    @classmethod
    def parse_resume_bytes(cls, pdf_bytes: bytes) -> Dict[str, Any]:
        text = cls.extract_text_from_pdf(pdf_bytes)
        parsed = cls.parse_resume_text(text)
        parsed["raw_text_preview"] = text[:1500] if len(text) > 1500 else text
        return parsed

    # ---------------------------------------------------------------
    # Section & Entity Extraction Helpers
    # ---------------------------------------------------------------
    @staticmethod
    def _extract_email(text: str) -> Optional[str]:
        match = re.search(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}", text)
        return match.group(0).lower() if match else None

    @staticmethod
    def _extract_phone(text: str) -> Optional[str]:
        match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        return match.group(0).strip() if match else None

    @staticmethod
    def _extract_name(lines: List[str], email: Optional[str]) -> Optional[str]:
        # The name is almost always at the very top of a resume
        invalid_starters = [
            "resume", "curriculum", "vitae", "cv", "page", "contact",
            "email", "phone", "address", "linkedin", "github", "portfolio",
            "http", "https", "education", "experience", "skills", "objective",
        ]
        for line in lines[:5]:
            clean = line.strip()
            # If line contains email or phone, skip it
            if email and email in clean.lower():
                continue
            if re.search(r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}", clean):
                continue
            lower = clean.lower()
            if any(lower.startswith(w) for w in invalid_starters):
                continue
            # Names typically consist of 2-4 words, alphabet letters and dots/spaces
            words = clean.split()
            if 1 <= len(words) <= 4 and re.match(r"^[A-Za-z\s\.\,\'-]+$", clean):
                return clean.title()
        return None

    @staticmethod
    def _extract_college(text: str) -> Optional[str]:
        target_words = r"(?:University|Institute of Technology|College of Engineering|College|Polytechnic|Academy)"
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        for line in lines:
            if line.upper() in ["EDUCATION", "ACADEMICS", "ACADEMIC BACKGROUND", "EDUCATIONAL BACKGROUND"]:
                continue
            clean_line = re.sub(r"(?i)^(?:education|academics|college|university)[\s:\-]+", "", line).strip()

            # Direct well-known patterns
            m1 = re.search(r"(?i)\b(National Institute of Technology[A-Za-z\t ,]*)\b", clean_line)
            if m1:
                cand = m1.group(1).strip()
                words = cand.split()
                return " ".join([w.lower() if w.lower() in ["of", "and", "in", "the", "for"] and i > 0 else w.capitalize() for i, w in enumerate(words)])

            m2 = re.search(r"(?i)\b(Indian Institute of Technology[A-Za-z\t ,]*)\b", clean_line)
            if m2:
                cand = m2.group(1).strip()
                words = cand.split()
                return " ".join([w.lower() if w.lower() in ["of", "and", "in", "the", "for"] and i > 0 else w.capitalize() for i, w in enumerate(words)])

            m3 = re.search(r"(?i)\b(Stanford University|Harvard University|MIT|UC Berkeley|Carnegie Mellon University)\b", clean_line)
            if m3:
                return m3.group(1).strip()

            # General college pattern on a single line
            m = re.search(rf"(?i)\b([A-Z][A-Za-z\t ,]+{target_words}(?:[A-Za-z\t ,]+)?)\b", clean_line)
            if m:
                cand = m.group(1).strip()
                if 5 < len(cand) < 80:
                    words = cand.split()
                    return " ".join([w.lower() if w.lower() in ["of", "and", "in", "the", "for"] and i > 0 else w.capitalize() for i, w in enumerate(words)])

        return None

    @staticmethod
    def _extract_degree(text: str) -> Optional[str]:
        degrees = [
            (r"(?i)\b(?:b\.?\s?tech|bachelor of technology)\b", "B.Tech / B.E."),
            (r"(?i)\b(?:b\.?\s?e\.?|bachelor of engineering)\b", "B.Tech / B.E."),
            (r"(?i)\b(?:b\.?\s?s\.?|bachelor of science)\b", "B.S. / B.Sc."),
            (r"(?i)\b(?:m\.?\s?tech|master of technology)\b", "M.S. / M.Tech"),
            (r"(?i)\b(?:m\.?\s?s\.?|master of science)\b", "M.S. / M.Tech"),
            (r"(?i)\b(?:ph\.?d|doctor of philosophy)\b", "Ph.D."),
        ]
        for pattern, canonical_degree in degrees:
            if re.search(pattern, text):
                return canonical_degree
        return "B.Tech / B.E."

    @staticmethod
    def _extract_branch(text: str) -> Optional[str]:
        branches = [
            (r"(?i)\b(?:computer science(?: and engineering)?|cs|cse)\b", "Computer Science"),
            (r"(?i)\b(?:information technology|it)\b", "Information Technology"),
            (r"(?i)\b(?:artificial intelligence|data science|ai & ds)\b", "Artificial Intelligence & Data Science"),
            (r"(?i)\b(?:electrical(?: and electronics)? engineering|eee|ece)\b", "Electrical & Electronics Engineering"),
            (r"(?i)\b(?:mechanical engineering)\b", "Mechanical Engineering"),
            (r"(?i)\b(?:mathematics and computing)\b", "Mathematics & Computing"),
        ]
        for pattern, branch_name in branches:
            if re.search(pattern, text):
                return branch_name
        return "Computer Science"

    @staticmethod
    def _extract_gpa(text: str) -> Optional[float]:
        # Formats: GPA: 3.82, CGPA: 9.1, 3.82 / 4.0, 3.82/4.00, Grade: 3.82
        match = re.search(
            r"(?i)\b(?:c?gpa|grade|score)[\s:]*([0-9]{1,2}(?:\.[0-9]{1,2})?)(?:\s*\/\s*(?:4\.00?|10(?:\.0)?))?\b",
            text,
        )
        if match:
            try:
                val = float(match.group(1))
                if 0.0 <= val <= 10.0:
                    # Normalize 10-scale to 4-scale if > 4.0
                    if val > 4.0:
                        val = round(val / 2.5, 2)
                    return val
            except ValueError:
                pass

        # Fallback: find standalone "X.XX / 4.0"
        match2 = re.search(r"\b([0-4]\.[0-9]{1,2})\s*\/\s*4\.0", text)
        if match2:
            try:
                return float(match2.group(1))
            except ValueError:
                pass

        return None

    @staticmethod
    def _extract_academic_years(text: str) -> Tuple[Optional[str], Optional[str]]:
        # Academic year (e.g., 3rd Year, Sophomore, Senior)
        academic_year = None
        year_match = re.search(
            r"(?i)\b([1-4](?:st|nd|rd|th)?\s+year|freshman|sophomore|junior|senior|final year)\b",
            text,
        )
        if year_match:
            raw_yr = year_match.group(1).lower()
            if "1" in raw_yr or "freshman" in raw_yr:
                academic_year = "1st Year"
            elif "2" in raw_yr or "sophomore" in raw_yr:
                academic_year = "2nd Year"
            elif "3" in raw_yr or "junior" in raw_yr:
                academic_year = "3rd Year"
            elif "4" in raw_yr or "senior" in raw_yr or "final" in raw_yr:
                academic_year = "4th Year"

        # Graduation year
        grad_year = None
        grad_match = re.search(
            r"(?i)(?:expected|graduation|class of)[\s:]*(?:[a-zA-Z]+\s+)?(202[4-9]|203[0-5])\b",
            text,
        )
        if grad_match:
            grad_year = grad_match.group(1)
        else:
            # Look for 2024-2028
            year_matches = re.findall(r"\b(202[4-9]|203[0-2])\b", text)
            if year_matches:
                grad_year = sorted(year_matches)[-1]

        return academic_year, grad_year

    @staticmethod
    def _extract_summary(text: str, lines: List[str]) -> Optional[str]:
        # Search for summary / objective section
        match = re.search(
            r"(?i)(?:professional summary|summary|objective|about me)[\s:]*\n+([^\n]+(?:\n+[^\n]+){1,4})",
            text,
        )
        if match:
            clean = " ".join(match.group(1).split())
            if len(clean) > 20:
                return clean[:400]

        # Or first descriptive sentence from top section
        for line in lines[2:8]:
            if len(line) > 50 and not line.startswith("http") and "@" not in line:
                return line.strip()[:400]

        return None

    @classmethod
    def _extract_projects(cls, text: str) -> List[Dict[str, Any]]:
        projects: List[Dict[str, Any]] = []
        # Find PROJECTS section
        section_match = re.search(
            r"(?i)(?:projects|academic projects|personal projects|key projects)[\s:]*\n([\s\S]+?)(?=\n[A-Z\s]{4,}:|\Z)",
            text,
        )
        if not section_match:
            return projects

        content = section_match.group(1).strip()
        # Split by empty lines or bullet points
        blocks = re.split(r"\n\s*\n+", content)
        for block in blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue

            first_line = lines[0]
            # Strip dates and links from title
            title = re.sub(r"[\(\[].*?[\)\]]", "", first_line).strip()
            title = re.sub(r"(?i)(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{4}).*", "", title).strip()
            title = title.strip(" -:|•*")

            if not title or len(title) < 3 or len(title) > 80:
                continue

            description = " ".join(lines[1:]) if len(lines) > 1 else first_line
            # Extract skills used in this specific project block
            techs = SkillExtractionService.extract_skills_from_text(block)

            projects.append({
                "title": title,
                "description": description[:300],
                "technologies": techs[:6],
            })

            if len(projects) >= 4:
                break

        return projects

    @classmethod
    def _extract_experience(cls, text: str) -> List[Dict[str, Any]]:
        experience: List[Dict[str, Any]] = []
        section_match = re.search(
            r"(?i)(?:work experience|experience|employment history|internships)[\s:]*\n([\s\S]+?)(?=\n[A-Z\s]{4,}:|\Z)",
            text,
        )
        if not section_match:
            return experience

        content = section_match.group(1).strip()
        blocks = re.split(r"\n\s*\n+", content)
        for block in blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue

            headline = lines[0]
            role = headline
            org = "Organization"
            duration = "Past"

            # Check for delimiter like 'at', '|', or '-'
            if " at " in headline:
                parts = headline.split(" at ", 1)
                role = parts[0].strip()
                org = parts[1].strip()
            elif "|" in headline:
                parts = headline.split("|")
                role = parts[0].strip()
                if len(parts) > 1:
                    org = parts[1].strip()
            elif " - " in headline:
                parts = headline.split(" - ", 1)
                role = parts[0].strip()
                org = parts[1].strip()

            date_match = re.search(r"(?i)\b(?:20\d\d|present|current)\b", block)
            if date_match:
                duration = date_match.group(0)

            desc = " ".join(lines[1:]) if len(lines) > 1 else headline

            experience.append({
                "role": role[:60],
                "organization": org[:60],
                "duration": duration,
                "description": desc[:300],
            })

            if len(experience) >= 3:
                break

        return experience

    @classmethod
    def _extract_certifications(cls, text: str) -> List[Dict[str, Any]]:
        certs: List[Dict[str, Any]] = []
        section_match = re.search(
            r"(?i)(?:certifications|licenses & certifications|credentials)[\s:]*\n([\s\S]+?)(?=\n[A-Z\s]{4,}:|\Z)",
            text,
        )
        if not section_match:
            return certs

        content = section_match.group(1).strip()
        lines = [l.strip(" •*-") for l in content.split("\n") if l.strip()]
        for line in lines:
            if len(line) < 4:
                continue
            name = line
            issuer = "Verified Issuer"
            if " by " in line:
                parts = line.split(" by ", 1)
                name = parts[0].strip()
                issuer = parts[1].strip()
            elif " - " in line:
                parts = line.split(" - ", 1)
                name = parts[0].strip()
                issuer = parts[1].strip()
            elif "|" in line:
                parts = line.split("|", 1)
                name = parts[0].strip()
                issuer = parts[1].strip()

            date_match = re.search(r"\b(20\d\d)\b", line)
            issue_date = date_match.group(1) if date_match else "Verified"

            certs.append({
                "name": name[:80],
                "issuing_organization": issuer[:60],
                "issue_date": issue_date,
            })

            if len(certs) >= 4:
                break

        return certs
