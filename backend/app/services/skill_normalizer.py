import re
from typing import Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session
from app.models.skill import Skill, StudentSkill

# Canonical Skills Taxonomy: Canonical Name -> Category
CANONICAL_SKILLS: Dict[str, str] = {
    # Programming Languages
    "Python": "Programming Languages",
    "JavaScript": "Programming Languages",
    "TypeScript": "Programming Languages",
    "Java": "Programming Languages",
    "C++": "Programming Languages",
    "C#": "Programming Languages",
    "C": "Programming Languages",
    "Go": "Programming Languages",
    "Rust": "Programming Languages",
    "Ruby": "Programming Languages",
    "PHP": "Programming Languages",
    "Swift": "Programming Languages",
    "Kotlin": "Programming Languages",
    "R": "Programming Languages",
    "MATLAB": "Programming Languages",
    "Scala": "Programming Languages",
    "Dart": "Programming Languages",
    "Shell Scripting": "Programming Languages",
    "Bash": "Programming Languages",
    "SQL": "Programming Languages",
    "HTML": "Web Technologies",
    "CSS": "Web Technologies",

    # Frameworks & Libraries
    "React": "Frameworks & Libraries",
    "Node.js": "Frameworks & Libraries",
    "Express.js": "Frameworks & Libraries",
    "Next.js": "Frameworks & Libraries",
    "Vue.js": "Frameworks & Libraries",
    "Angular": "Frameworks & Libraries",
    "Django": "Frameworks & Libraries",
    "FastAPI": "Frameworks & Libraries",
    "Flask": "Frameworks & Libraries",
    "Spring Boot": "Frameworks & Libraries",
    "ASP.NET": "Frameworks & Libraries",
    ".NET": "Frameworks & Libraries",
    "TailwindCSS": "Frameworks & Libraries",
    "Bootstrap": "Frameworks & Libraries",
    "GraphQL": "Frameworks & Libraries",
    "REST APIs": "Frameworks & Libraries",

    # AI, Machine Learning & Data Science
    "Machine Learning": "AI & Machine Learning",
    "Deep Learning": "AI & Machine Learning",
    "Artificial Intelligence": "AI & Machine Learning",
    "Natural Language Processing": "AI & Machine Learning",
    "Computer Vision": "AI & Machine Learning",
    "PyTorch": "AI & Machine Learning",
    "TensorFlow": "AI & Machine Learning",
    "Keras": "AI & Machine Learning",
    "Scikit-Learn": "AI & Machine Learning",
    "Pandas": "Data Science & Analytics",
    "NumPy": "Data Science & Analytics",
    "JAX": "AI & Machine Learning",
    "Hugging Face": "AI & Machine Learning",
    "Large Language Models": "AI & Machine Learning",
    "Transformers": "AI & Machine Learning",
    "LangChain": "AI & Machine Learning",
    "Data Science": "Data Science & Analytics",
    "Data Analysis": "Data Science & Analytics",
    "Data Engineering": "Data Science & Analytics",
    "Apache Spark": "Data Science & Analytics",
    "Apache Kafka": "Data Science & Analytics",
    "Hadoop": "Data Science & Analytics",
    "Tableau": "Data Science & Analytics",
    "Power BI": "Data Science & Analytics",

    # Databases & Storage
    "PostgreSQL": "Databases",
    "MySQL": "Databases",
    "MongoDB": "Databases",
    "Redis": "Databases",
    "SQLite": "Databases",
    "Oracle": "Databases",
    "Cassandra": "Databases",
    "DynamoDB": "Databases",
    "Elasticsearch": "Databases",
    "Firebase": "Databases",

    # Cloud & DevOps
    "AWS": "Cloud & DevOps",
    "Google Cloud": "Cloud & DevOps",
    "Azure": "Cloud & DevOps",
    "Docker": "Cloud & DevOps",
    "Kubernetes": "Cloud & DevOps",
    "CI/CD": "Cloud & DevOps",
    "GitHub Actions": "Cloud & DevOps",
    "Jenkins": "Cloud & DevOps",
    "Terraform": "Cloud & DevOps",
    "Ansible": "Cloud & DevOps",
    "Linux": "Operating Systems & Tools",
    "Git": "Operating Systems & Tools",
    "GitHub": "Operating Systems & Tools",
    "GitLab": "Operating Systems & Tools",

    # Core CS & Systems
    "Data Structures & Algorithms": "Core Computer Science",
    "Object-Oriented Programming": "Core Computer Science",
    "Distributed Systems": "Core Computer Science",
    "System Design": "Core Computer Science",
    "Computer Networks": "Core Computer Science",
    "Operating Systems": "Core Computer Science",
    "Cybersecurity": "Cybersecurity & Networks",
    "Microservices": "Architecture & Engineering",
    "Unit Testing": "Quality Assurance & Testing",
    "Agile Methodology": "Project Management",

    # Mechanical Engineering
    "CAD": "Mechanical Engineering",
    "SolidWorks": "Mechanical Engineering",
    "AutoCAD": "Mechanical Engineering",
    "CATIA": "Mechanical Engineering",
    "ANSYS": "Mechanical Engineering",
    "Finite Element Analysis": "Mechanical Engineering",
    "Thermodynamics": "Mechanical Engineering",
    "Fluid Mechanics": "Mechanical Engineering",
    "Computational Fluid Dynamics": "Mechanical Engineering",
    "GD&T": "Mechanical Engineering",
    "DFM": "Mechanical Engineering",
    "Robotics": "Mechanical Engineering",
    "ROS": "Mechanical Engineering",
    "Mechatronics": "Mechanical Engineering",
    "Materials Science": "Mechanical Engineering",
    "Additive Manufacturing": "Mechanical Engineering",
    "Kinematics": "Mechanical Engineering",
    "HVAC": "Mechanical Engineering",
    "EV Powertrain": "Mechanical Engineering",

    # Electrical & Electronics Engineering
    "Embedded Systems": "Electrical & Electronics",
    "Embedded C": "Electrical & Electronics",
    "Microcontrollers": "Electrical & Electronics",
    "STM32": "Electrical & Electronics",
    "ESP32": "Electrical & Electronics",
    "Arduino": "Electrical & Electronics",
    "RTOS": "Electrical & Electronics",
    "Circuit Design": "Electrical & Electronics",
    "PCB Design": "Electrical & Electronics",
    "Altium Designer": "Electrical & Electronics",
    "KiCad": "Electrical & Electronics",
    "Verilog": "Electrical & Electronics",
    "VHDL": "Electrical & Electronics",
    "FPGA": "Electrical & Electronics",
    "VLSI": "Electrical & Electronics",
    "Digital Electronics": "Electrical & Electronics",
    "Power Electronics": "Electrical & Electronics",
    "Signal Processing": "Electrical & Electronics",
    "IoT": "Electrical & Electronics",
    "Hardware Debugging": "Electrical & Electronics",

    # Finance, Business & Analytics
    "Financial Modeling": "Finance & Economics",
    "Valuation": "Finance & Economics",
    "DCF": "Finance & Economics",
    "LBO": "Finance & Economics",
    "Corporate Finance": "Finance & Economics",
    "Excel": "Finance & Economics",
    "VBA": "Finance & Economics",
    "Equity Research": "Finance & Economics",
    "Financial Statement Analysis": "Finance & Economics",
    "Accounting": "Finance & Economics",
    "Quantitative Finance": "Finance & Economics",
    "Algorithmic Trading": "Finance & Economics",
    "Portfolio Management": "Finance & Economics",
    "Risk Management": "Finance & Economics",
    "Investment Banking": "Finance & Economics",
    "Bloomberg Terminal": "Finance & Economics",
}

# Alias Map: normalized/lowercase variant -> Canonical Name
ALIAS_MAP: Dict[str, str] = {
    # ML variations
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "machine-learning": "Machine Learning",
    "machinelearning": "Machine Learning",
    "ai/ml": "Machine Learning",
    "aiml": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "deep-learning": "Deep Learning",
    "deeplearning": "Deep Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "artificial-intelligence": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "llm": "Large Language Models",
    "llms": "Large Language Models",
    "large language models": "Large Language Models",
    "genai": "Artificial Intelligence",
    "generative ai": "Artificial Intelligence",

    # JS & Frontend variations
    "js": "JavaScript",
    "javascript": "JavaScript",
    "java script": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "type script": "TypeScript",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react js": "React",
    "react-js": "React",
    "react native": "React",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "angular.js": "Angular",
    "tailwind": "TailwindCSS",
    "tailwindcss": "TailwindCSS",
    "tailwind css": "TailwindCSS",
    "html5": "HTML",
    "html": "HTML",
    "css3": "CSS",
    "css": "CSS",

    # Database variations
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "postgres sql": "PostgreSQL",
    "postgre": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "sqlite3": "SQLite",
    "elastic": "Elasticsearch",
    "elasticsearch": "Elasticsearch",

    # Python & AI libraries
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "sklearn": "Scikit-Learn",
    "scikit-learn": "Scikit-Learn",
    "scikitlearn": "Scikit-Learn",
    "scikit learn": "Scikit-Learn",
    "pd": "Pandas",
    "pandas": "Pandas",
    "np": "NumPy",
    "numpy": "NumPy",
    "huggingface": "Hugging Face",
    "hugging face": "Hugging Face",

    # Cloud & DevOps variations
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "google cloud": "Google Cloud",
    "azure": "Azure",
    "ms azure": "Azure",
    "microsoft azure": "Azure",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "containerization": "Docker",
    "containers": "Docker",
    "cicd": "CI/CD",
    "ci/cd": "CI/CD",
    "ci-cd": "CI/CD",
    "continuous integration": "CI/CD",
    "github actions": "GitHub Actions",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "git & github": "Git",

    # Languages & Systems variations
    "cpp": "C++",
    "c++": "C++",
    "c plus plus": "C++",
    "c#": "C#",
    "csharp": "C#",
    "c-sharp": "C#",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "java": "Java",
    "kotlin": "Kotlin",
    "scala": "Scala",
    "swift": "Swift",
    "ruby": "Ruby",
    "php": "PHP",
    "dotnet": ".NET",
    ".net": ".NET",
    "asp.net": "ASP.NET",
    "aspnet": "ASP.NET",
    "bash": "Bash",
    "shell": "Shell Scripting",
    "shell scripting": "Shell Scripting",
    "linux": "Linux",
    "unix": "Linux",
    "rest": "REST APIs",
    "restful": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "graphql": "GraphQL",
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "kafka": "Apache Kafka",
    "apache kafka": "Apache Kafka",

    # Core CS
    "dsa": "Data Structures & Algorithms",
    "data structures": "Data Structures & Algorithms",
    "algorithms": "Data Structures & Algorithms",
    "data structures & algorithms": "Data Structures & Algorithms",
    "data structures and algorithms": "Data Structures & Algorithms",
    "oop": "Object-Oriented Programming",
    "object oriented programming": "Object-Oriented Programming",
    "computer networks": "Computer Networks",
    "networking": "Computer Networks",

    # Mechanical aliases
    "solidworks": "SolidWorks",
    "solid works": "SolidWorks",
    "autocad": "AutoCAD",
    "auto cad": "AutoCAD",
    "cad": "CAD",
    "computer aided design": "CAD",
    "ansys": "ANSYS",
    "fea": "Finite Element Analysis",
    "finite element analysis": "Finite Element Analysis",
    "thermo": "Thermodynamics",
    "thermodynamics": "Thermodynamics",
    "cfd": "Computational Fluid Dynamics",
    "fluid mechanics": "Fluid Mechanics",
    "gd&t": "GD&T",
    "gdt": "GD&T",
    "dfm": "DFM",
    "dfa": "DFM",
    "robotics": "Robotics",
    "ros": "ROS",
    "mechatronics": "Mechatronics",
    "materials science": "Materials Science",
    "ev powertrain": "EV Powertrain",
    "hvac": "HVAC",

    # Electrical & Electronics aliases
    "embedded": "Embedded Systems",
    "embedded systems": "Embedded Systems",
    "embedded c": "Embedded C",
    "embedded c/c++": "Embedded C",
    "microcontroller": "Microcontrollers",
    "microcontrollers": "Microcontrollers",
    "stm32": "STM32",
    "esp32": "ESP32",
    "arduino": "Arduino",
    "rtos": "RTOS",
    "real time operating system": "RTOS",
    "pcb": "PCB Design",
    "pcb design": "PCB Design",
    "altium": "Altium Designer",
    "altium designer": "Altium Designer",
    "kicad": "KiCad",
    "verilog": "Verilog",
    "vhdl": "VHDL",
    "fpga": "FPGA",
    "vlsi": "VLSI",
    "circuit design": "Circuit Design",
    "power electronics": "Power Electronics",
    "signal processing": "Signal Processing",
    "dsp": "Signal Processing",
    "iot": "IoT",
    "internet of things": "IoT",

    # Finance aliases
    "financial modeling": "Financial Modeling",
    "financial model": "Financial Modeling",
    "valuation": "Valuation",
    "dcf": "DCF",
    "lbo": "LBO",
    "corporate finance": "Corporate Finance",
    "excel": "Excel",
    "ms excel": "Excel",
    "vba": "VBA",
    "equity research": "Equity Research",
    "financial statement analysis": "Financial Statement Analysis",
    "accounting": "Accounting",
    "quant": "Quantitative Finance",
    "quantitative finance": "Quantitative Finance",
    "algo trading": "Algorithmic Trading",
    "algorithmic trading": "Algorithmic Trading",
    "investment banking": "Investment Banking",
    "risk management": "Risk Management",
    "portfolio management": "Portfolio Management",
    "bloomberg": "Bloomberg Terminal",
}


class SkillNormalizationService:
    @staticmethod
    def clean_token(name: str) -> str:
        """Strip surrounding whitespaces, lowercase, and normalize punctuation."""
        if not name:
            return ""
        cleaned = name.strip().lower()
        # Keep dots in .net, node.js, react.js, and pluses in c++, hashes in c#
        # Normalize multiple spaces, hyphens, and underscores to single space if not in special names
        if cleaned in ["c++", "c#", ".net", "node.js", "react.js", "next.js", "vue.js", "ci/cd"]:
            return cleaned
        cleaned = re.sub(r"[\t\r\n]+", " ", cleaned)
        cleaned = re.sub(r"[-_]+", " ", cleaned)
        cleaned = re.sub(r"[^\w\s\+\#\.\/]", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    @classmethod
    def normalize(cls, raw_name: str) -> str:
        """
        Deterministically normalizes any skill variation to its canonical name.
        Example:
            ML -> Machine Learning
            machine-learning -> Machine Learning
            JS -> JavaScript
            ReactJS -> React
            Postgres -> PostgreSQL
        """
        if not raw_name or not raw_name.strip():
            return ""

        raw_trimmed = raw_name.strip()
        direct_key = raw_trimmed.lower()

        # 1. Check direct alias lookup
        if direct_key in ALIAS_MAP:
            return ALIAS_MAP[direct_key]

        # 2. Check cleaned token
        cleaned_key = cls.clean_token(raw_trimmed)
        if cleaned_key in ALIAS_MAP:
            return ALIAS_MAP[cleaned_key]

        # 3. Check if clean key matches any canonical skill case-insensitively
        for canonical in CANONICAL_SKILLS:
            if canonical.lower() == cleaned_key or canonical.lower() == direct_key:
                return canonical

        # 4. Check if variation without spaces/hyphens matches alias (e.g. machinelearning)
        compressed_key = re.sub(r"[\s\-_]+", "", direct_key)
        if compressed_key in ALIAS_MAP:
            return ALIAS_MAP[compressed_key]

        # 5. Default fallback: Clean and Title-case words, preserving known acronyms
        words = cleaned_key.split()
        title_words = []
        for w in words:
            if w.upper() in ["AI", "ML", "SQL", "AWS", "GCP", "API", "APIS", "UI", "UX", "CI", "CD", "CSS", "HTML", "PHP"]:
                title_words.append(w.upper())
            else:
                title_words.append(w.capitalize())
        return " ".join(title_words) if title_words else raw_trimmed

    @classmethod
    def normalize_list(cls, raw_skills: List[str]) -> List[str]:
        """
        Normalizes a list of skills, recognizes aliases, deduplicates,
        and preserves first-seen canonical order.
        """
        seen: Set[str] = set()
        normalized_list: List[str] = []

        for item in raw_skills:
            if not item:
                continue
            canonical = cls.normalize(item)
            if canonical and canonical.lower() not in seen:
                seen.add(canonical.lower())
                normalized_list.append(canonical)

        return normalized_list

    @classmethod
    def get_category_for_skill(cls, canonical_name: str) -> str:
        return CANONICAL_SKILLS.get(canonical_name, "Technical Skills")

    @classmethod
    def get_or_create_canonical_skill(cls, db: Session, raw_name: str) -> Skill:
        """
        Retrieves existing canonical skill or creates and persists a new Skill record.
        Maintains unique canonical normalized_name in the database.
        """
        canonical_name = cls.normalize(raw_name)
        norm_key = canonical_name.lower().strip()

        # Check by normalized_name first
        skill = db.query(Skill).filter(Skill.normalized_name == norm_key).first()
        if not skill:
            # Check by exact name as fallback
            skill = db.query(Skill).filter(Skill.name.ilike(canonical_name)).first()

        if not skill:
            category = cls.get_category_for_skill(canonical_name)
            skill = Skill(
                name=canonical_name,
                normalized_name=norm_key,
                category=category,
                description=f"Verified competency in {canonical_name}.",
            )
            db.add(skill)
            db.flush()

        return skill

    @classmethod
    def add_skill_to_student(
        cls,
        db: Session,
        student_profile_id: str,
        raw_name: str,
        proficiency: str = "Beginner",
        verified: bool = False,
        verified_via: Optional[str] = None,
    ) -> Tuple[StudentSkill, bool]:
        """
        Safely attaches normalized skill to student profile preventing duplicate logical skills.
        Returns tuple of (StudentSkill, is_created: bool).
        """
        canonical_skill = cls.get_or_create_canonical_skill(db, raw_name)

        existing = (
            db.query(StudentSkill)
            .filter(
                StudentSkill.student_profile_id == student_profile_id,
                StudentSkill.skill_id == canonical_skill.id,
            )
            .first()
        )

        if existing:
            # Update proficiency if higher or updated, but do not create duplicate
            if proficiency and proficiency != existing.proficiency:
                existing.proficiency = proficiency
            if verified:
                existing.verified = True
                if verified_via:
                    existing.verified_via = verified_via
            db.flush()
            return existing, False

        new_student_skill = StudentSkill(
            student_profile_id=student_profile_id,
            skill_id=canonical_skill.id,
            proficiency=proficiency,
            verified=verified,
            verified_via=verified_via,
        )
        db.add(new_student_skill)
        db.flush()
        return new_student_skill, True
