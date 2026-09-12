from enum import Enum


class UserRole(str, Enum):
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"
    # Additional roles can be added here in the future (e.g., EMPLOYER, MENTOR)


class OpportunityCategory(str, Enum):
    INTERNSHIP = "INTERNSHIP"
    HACKATHON = "HACKATHON"
    SCHOLARSHIP = "SCHOLARSHIP"
    COURSE = "COURSE"
    PROJECT = "PROJECT"
    JOB = "JOB"
    SKILL_OPPORTUNITY = "SKILL_OPPORTUNITY"


class ApplicationStatus(str, Enum):
    SAVED = "SAVED"
    PLANNING = "PLANNING"
    DOING = "DOING"
    PENDING = "PENDING"
    APPLIED = "APPLIED"
    SHORTLISTED = "SHORTLISTED"
    INTERVIEW = "INTERVIEW"
    SELECTED = "SELECTED"
    COMPLETED = "COMPLETED"
    NOT_COMPLETED = "NOT_COMPLETED"
    ISSUED = "ISSUED"
    REJECTED = "REJECTED"

class OpportunityStatus(str, Enum):
    UNMARKED = "UNMARKED"
    ISSUED = "ISSUED"
    COMPLETED = "COMPLETED"
    NOT_COMPLETED = "NOT_COMPLETED"
    PENDING = "PENDING"


class WorkMode(str, Enum):
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ONSITE = "On-site"
    ONLINE = "Online"
    FLEXIBLE = "Flexible / Remote"


class EligibilityStatus(str, Enum):
    ELIGIBLE = "Eligible"
    PARTIALLY_ELIGIBLE = "Partially Eligible"
    NOT_ELIGIBLE = "Not Eligible"
    UNKNOWN = "Unknown"


class SkillLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    ESSENTIAL = "Essential"


class NotificationType(str, Enum):
    MATCH = "match"
    DEADLINE = "deadline"
    APPLICATION = "application"
    SYSTEM = "system"
