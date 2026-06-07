import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import get_database
from app.core.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, hash_token,
    get_current_user, REFRESH_TOKEN_EXPIRE_DAYS
)
from app.models.user import User, UserRole
from app.models.token import RefreshToken
import uuid, logging
from datetime import timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Schemas ──────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.ANALYST

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

# ── Routes ───────────────────────────────────────────────────

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_database)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    if len(body.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")
    user = User(
        id=uuid.uuid4(),
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        role=body.role,
        is_active=True,
        is_verified=True,  # skip email verify for now
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info(f"New user registered: {user.email} role={user.role}")
    return UserResponse(
        id=str(user.id), email=user.email, full_name=user.full_name,
        role=user.role, is_active=user.is_active, is_verified=user.is_verified,
        created_at=user.created_at
    )

@router.post("/login")
async def login(body: LoginRequest, request: Request, response: Response, db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(User).where(User.email == body.email, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token  = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    refresh_token = create_refresh_token()
    token_hash    = hash_token(refresh_token)
    expires_at    = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    db_token = RefreshToken(
        id=uuid.uuid4(), user_id=user.id, token_hash=token_hash,
        expires_at=expires_at, ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    )
    db.add(db_token)
    await db.execute(update(User).where(User.id == user.id).values(last_login=datetime.utcnow()))
    await db.commit()

    response.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, secure=False, samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400, path="/api/auth/refresh"
    )

    logger.info(f"User logged in: {user.email}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 900,
        "user": {
            "id": str(user.id), "email": user.email,
            "full_name": user.full_name, "role": user.role
        }
    }

@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_database)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    token_hash = hash_token(token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        )
    )
    db_token = result.scalar_one_or_none()
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_result = await db.execute(select(User).where(User.id == db_token.user_id, User.is_active == True))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Rotate refresh token
    new_refresh = create_refresh_token()
    new_hash    = hash_token(new_refresh)
    db_token.revoked = True
    new_db_token = RefreshToken(
        id=uuid.uuid4(), user_id=user.id, token_hash=new_hash,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    )
    db.add(new_db_token)
    await db.commit()

    new_access = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    response.set_cookie(
        key="refresh_token", value=new_refresh,
        httponly=True, secure=False, samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400, path="/api/auth/refresh"
    )
    return {"access_token": new_access, "token_type": "bearer", "expires_in": 900}

@router.post("/logout")
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_database)):
    token = request.cookies.get("refresh_token")
    if token:
        token_hash = hash_token(token)
        await db.execute(
            update(RefreshToken).where(RefreshToken.token_hash == token_hash).values(revoked=True)
        )
        await db.commit()
    response.delete_cookie("refresh_token", path="/api/auth/refresh")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_user)):
    return UserResponse(
        id=str(user.id), email=user.email, full_name=user.full_name,
        role=user.role, is_active=user.is_active, is_verified=user.is_verified,
        created_at=user.created_at
    )

@router.get("/health")
async def auth_health():
    return {"status": "ok", "service": "auth"}
