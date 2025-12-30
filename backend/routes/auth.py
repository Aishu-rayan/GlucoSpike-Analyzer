"""
Authentication routes for user registration, login, and session management.
Uses cookie-based sessions with bcrypt password hashing.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import get_db
from db.models import User, Profile, Session

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Session configuration
SESSION_COOKIE_NAME = "glucoguide_session"
SESSION_EXPIRE_HOURS = 24 * 7  # 7 days


# ============================================================================
# Schemas
# ============================================================================

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    has_profile: bool
    onboarding_completed: bool

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    message: str
    user: Optional[UserResponse] = None


# ============================================================================
# Password utilities
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


# ============================================================================
# Session utilities
# ============================================================================

def generate_session_id() -> str:
    """Generate a secure random session ID"""
    return secrets.token_hex(32)


async def create_session(db: AsyncSession, user_id: int) -> str:
    """Create a new session for a user"""
    session_id = generate_session_id()
    expires_at = datetime.utcnow() + timedelta(hours=SESSION_EXPIRE_HOURS)
    
    session = Session(
        id=session_id,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(session)
    await db.flush()
    
    return session_id


async def get_session(db: AsyncSession, session_id: str) -> Optional[Session]:
    """Get a valid session by ID"""
    if not session_id:
        return None
    
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.expires_at > datetime.utcnow()
        )
    )
    return result.scalar_one_or_none()


async def delete_session(db: AsyncSession, session_id: str):
    """Delete a session"""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if session:
        await db.delete(session)


async def cleanup_expired_sessions(db: AsyncSession):
    """Remove expired sessions"""
    result = await db.execute(
        select(Session).where(Session.expires_at <= datetime.utcnow())
    )
    expired = result.scalars().all()
    for session in expired:
        await db.delete(session)


# ============================================================================
# Auth dependency
# ============================================================================

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
) -> User:
    """Get the current authenticated user from session cookie"""
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = await get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    
    result = await db.execute(select(User).where(User.id == session.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
) -> Optional[User]:
    """Get the current user if authenticated, None otherwise"""
    if not session_id:
        return None
    
    session = await get_session(db, session_id)
    if not session:
        return None
    
    result = await db.execute(select(User).where(User.id == session.user_id))
    return result.scalar_one_or_none()


# ============================================================================
# Routes
# ============================================================================

@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account"""
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == request.username.lower())
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    user = User(
        username=request.username.lower(),
        password_hash=hash_password(request.password),
    )
    db.add(user)
    await db.flush()
    
    # Create empty profile
    profile = Profile(user_id=user.id)
    db.add(profile)
    
    # Create session
    session_id = await create_session(db, user.id)
    
    # Set session cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        max_age=SESSION_EXPIRE_HOURS * 3600,
        samesite="lax",
    )
    
    await db.commit()
    
    return AuthResponse(
        message="Registration successful",
        user=UserResponse(
            id=user.id,
            username=user.username,
            created_at=user.created_at,
            has_profile=True,
            onboarding_completed=False,
        )
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Log in with username and password"""
    # Find user
    result = await db.execute(
        select(User).where(User.username == request.username.lower())
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    
    # Create session
    session_id = await create_session(db, user.id)
    
    # Set session cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        max_age=SESSION_EXPIRE_HOURS * 3600,
        samesite="lax",
    )
    
    # Check if user has profile
    profile_result = await db.execute(
        select(Profile).where(Profile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    
    await db.commit()
    
    return AuthResponse(
        message="Login successful",
        user=UserResponse(
            id=user.id,
            username=user.username,
            created_at=user.created_at,
            has_profile=profile is not None,
            onboarding_completed=profile.onboarding_completed if profile else False,
        )
    )


@router.post("/logout", response_model=AuthResponse)
async def logout(
    response: Response,
    db: AsyncSession = Depends(get_db),
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
):
    """Log out and invalidate session"""
    if session_id:
        await delete_session(db, session_id)
        await db.commit()
    
    # Clear session cookie
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    
    return AuthResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def get_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current authenticated user"""
    # Check if user has profile
    profile_result = await db.execute(
        select(Profile).where(Profile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at,
        has_profile=profile is not None,
        onboarding_completed=profile.onboarding_completed if profile else False,
    )


@router.get("/check")
async def check_auth(
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Check if user is authenticated (doesn't require auth)"""
    return {
        "authenticated": current_user is not None,
        "user_id": current_user.id if current_user else None,
        "username": current_user.username if current_user else None,
    }

