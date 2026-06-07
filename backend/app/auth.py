from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from .core.database import get_database
from .models.user import User
import os

SECRET = os.environ.get("SECRET_KEY", "change_this_in_production")

cookie_transport = CookieTransport(cookie_name="auth_cookie", cookie_max_age=3600, cookie_httponly=True, cookie_secure=False)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

async def get_user_db(session: AsyncSession = Depends(get_database)):
    yield SQLAlchemyUserDatabase(session, User)

fastapi_users = FastAPIUsers[User, int](get_user_db, [auth_backend])

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)

def require_role(allowed_roles):
    async def role_checker(user: User = Depends(current_user)):
        if user.role not in allowed_roles:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return role_checker
