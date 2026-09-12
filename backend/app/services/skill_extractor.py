import re
from typing import List, Set
from app.services.skill_normalizer import ALIAS_MAP, CANONICAL_SKILLS, SkillNormalizationService


class SkillExtractionService:
    # Pre-compiled search terms grouped by complexity
    _SPECIAL_SYMBOLS = [
        (re.compile(r"(?i)\bc\+\+\b"), "C++"),
        (re.compile(r"(?i)\bc\#\b"), "C#"),
        (re.compile(r"(?i)(?:\b|\s)\.net\b"), ".NET"),
        (re.compile(r"(?i)\bnode\.js\b"), "Node.js"),
        (re.compile(r"(?i)\breact\.js\b"), "React"),
        (re.compile(r"(?i)\bnext\.js\b"), "Next.js"),
        (re.compile(r"(?i)\bvue\.js\b"), "Vue.js"),
        (re.compile(r"(?i)\bci\/cd\b"), "CI/CD"),
    ]

    # Contextual patterns for ambiguous short tokens
    _CONTEXTUAL_PATTERNS = [
        (re.compile(r"(?i)\b(?:languages?|technologies|skills|stacks?)\b[^\n]*\b(go|golang)\b"), "Go"),
        (re.compile(r"(?i)\b(golang)\b"), "Go"),
        (re.compile(r"(?i)\b(c\/c\+\+|c\s*,\s*c\+\+|c\s+and\s+c\+\+)\b"), "C"),
        (re.compile(r"(?i)\b(r\s+programming|r\s+studio|r\/python|python\/r)\b"), "R"),
    ]

    @classmethod
    def _build_term_regexes(cls):
        """Compile phrase regexes sorted by length descending so multi-word phrases match first."""
        all_phrases: Set[str] = set()
        for phrase in CANONICAL_SKILLS:
            all_phrases.add(phrase)
        for alias in ALIAS_MAP:
            # Skip 1-char tokens from raw regex (handled in contextual)
            if len(alias) >= 2 and alias not in ["c++", "c#", ".net", "ci/cd"]:
                all_phrases.add(alias)

        # Sort longer phrases first to avoid sub-match collisions
        sorted_phrases = sorted(all_phrases, key=lambda p: len(p), reverse=True)

        # Group into multi-word and single-word regexes
        multi_word = [p for p in sorted_phrases if " " in p or "-" in p or "&" in p or "/" in p]
        single_word = [p for p in sorted_phrases if " " not in p and "-" not in p and "&" not in p and "/" not in p]

        multi_patterns = []
        for p in multi_word:
            escaped = re.escape(p).replace(r"\ ", r"\s+").replace(r"\-", r"[\s\-]+").replace(r"\&", r"(?:\&|and)")
            pattern = re.compile(rf"(?i)\b{escaped}\b")
            multi_patterns.append((pattern, p))

        single_patterns = []
        for p in single_word:
            pattern = re.compile(rf"(?i)\b{re.escape(p)}\b")
            single_patterns.append((pattern, p))

        return multi_patterns, single_patterns

    _multi_patterns = None
    _single_patterns = None

    @classmethod
    def _init_patterns(cls):
        if cls._multi_patterns is None or cls._single_patterns is None:
            cls._multi_patterns, cls._single_patterns = cls._build_term_regexes()

    @classmethod
    def extract_skills_from_text(cls, text: str) -> List[str]:
        """
        Extracts and normalizes technical and relevant professional skills from unstructured text.
        Returns unique list of canonical skill names.
        """
        if not text or not text.strip():
            return []

        cls._init_patterns()
        found_skills: List[str] = []
        lower_text = text.lower()

        # 1. Check special symbol patterns first (C++, C#, .NET, CI/CD, Node.js, etc.)
        for pattern, canonical_candidate in cls._SPECIAL_SYMBOLS:
            if pattern.search(text):
                found_skills.append(canonical_candidate)

        # 2. Check contextual short tokens (Go, C, R)
        for pattern, canonical_candidate in cls._CONTEXTUAL_PATTERNS:
            if pattern.search(text):
                found_skills.append(canonical_candidate)

        # 3. Check multi-word phrase patterns
        for pattern, raw_term in cls._multi_patterns:
            if pattern.search(text):
                found_skills.append(raw_term)

        # 4. Check single-word patterns
        for pattern, raw_term in cls._single_patterns:
            # Special check for 'c' or 'r' to prevent false positive matching
            if raw_term.lower() in ["c", "r", "go"]:
                continue
            if pattern.search(text):
                found_skills.append(raw_term)

        # 5. Normalize all detected skills and deduplicate
        return SkillNormalizationService.normalize_list(found_skills)
