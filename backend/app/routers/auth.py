from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    Prevents duplicate emails and initializes a StudentProfile if registering as a student.
    Returns access token and user info.
    """
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    from urllib.parse import quote_plus
    safe_name = quote_plus(user_in.full_name.strip()) if user_in.full_name else "User"
    default_avatar = f"https://ui-avatars.com/api/?name={safe_name}&background=0284c7&color=fff&size=128&bold=true"

    user = User(
        email=user_in.email.lower(),
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        avatar_url=user_in.avatar_url or default_avatar,
    )
    db.add(user)
    db.flush()

    # Automatically initialize linked student profile
    college_name = user_in.college or user_in.university
    profile = StudentProfile(
        user_id=user.id,
        college=college_name,
        university=college_name,
        degree="B.Tech / B.E.",
        major="Computer Science",
        branch="Computer Science",
        academic_year="3rd Year",
        year="3rd Year",
        verified_profile_percent=85,
        profile_strength=80,
        match_confidence=88,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    prof = profile
    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
        avatarUrl=user.avatar_url,
        branch=prof.branch or prof.major if prof else None,
        academic_year=prof.academic_year or prof.year if prof else None,
    )
    return Token(access_token=token, token_type="bearer", user=user_resp)


@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user with email and password.
    Returns JWT access token.
    """
    user = db.query(User).filter(User.email == login_in.email.lower()).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive",
        )

    token = create_access_token(user.id)
    prof = user.student_profile or db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
        avatarUrl=user.avatar_url,
        branch=prof.branch or prof.major if prof else None,
        academic_year=prof.academic_year or prof.year if prof else None,
    )
    return Token(access_token=token, token_type="bearer", user=user_resp)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieve currently authenticated user information.
    """
    prof = current_user.student_profile or db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        avatar_url=current_user.avatar_url,
        avatarUrl=current_user.avatar_url,
        branch=prof.branch or prof.major if prof else None,
        academic_year=prof.academic_year or prof.year if prof else None,
    )
