from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillMatch API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./skillmatch.db"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars-long!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    FRONTEND_URL: Union[str, None] = None

    # AIML Matching Engine Weights (Sum to 1.0)
    MATCH_WEIGHT_SKILL: float = 0.40
    MATCH_WEIGHT_SEMANTIC: float = 0.25
    MATCH_WEIGHT_EDUCATION: float = 0.15
    MATCH_WEIGHT_INTERESTS: float = 0.10
    MATCH_WEIGHT_EXPERIENCE: float = 0.05
    MATCH_WEIGHT_PREFERENCES: float = 0.05

    # Embedding Model
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"

    # Optional Real LLM Integration (Gemini, OpenAI, Groq, OpenRouter)
    GEMINI_API_KEY: Union[str, None] = None
    OPENAI_API_KEY: Union[str, None] = None
    GROQ_API_KEY: Union[str, None] = None
    OPENROUTER_API_KEY: Union[str, None] = None
    AI_MODEL_NAME: str = "gemini-1.5-flash"

    @property
    def cors_origins_list(self) -> List[str]:
        origins: List[str] = []
        if isinstance(self.CORS_ORIGINS, list):
            origins.extend(self.CORS_ORIGINS)
        elif isinstance(self.CORS_ORIGINS, str):
            origins.extend([origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()])

        if self.FRONTEND_URL and self.FRONTEND_URL.strip():
            clean_front = self.FRONTEND_URL.strip().rstrip("/")
            if clean_front not in origins:
                origins.append(clean_front)

        # Default allowed origins for local dev and the primary Vercel deployment
        defaults = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "https://skill-match-o1b5.vercel.app",
        ]
        for d in defaults:
            if d not in origins:
                origins.append(d)

        return origins

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
