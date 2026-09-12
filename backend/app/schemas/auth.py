from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from app.models.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1)
    role: UserRole = UserRole.STUDENT
    avatar_url: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Allow 'name' as alias for 'full_name'
            if "name" in data and not data.get("full_name"):
                data["full_name"] = data["name"]
            # Allow case-insensitive role ('student', 'admin', etc.)
            if "role" in data and isinstance(data["role"], str):
                data["role"] = data["role"].upper()
        return data


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    college: Optional[str] = None
    university: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(UserBase):
    id: str
    is_active: bool
    name: Optional[str] = None
    avatarUrl: Optional[str] = None
    branch: Optional[str] = None
    academic_year: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
