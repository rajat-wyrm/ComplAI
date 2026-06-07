import asyncio, uuid
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.models.database import ASYNC_URL
from app.core.auth import hash_password

engine = create_async_engine(ASYNC_URL, connect_args={"ssl": True}, echo=False)

async def seed():
    async with engine.begin() as conn:
        # Check existing
        r = await conn.execute(text(
            "SELECT id FROM users WHERE email = 'admin@compliance.ai'"
        ))
        if r.fetchone():
            print("Admin already exists.")
            await engine.dispose()
            return

        uid = str(uuid.uuid4())
        hpw = hash_password("Admin@123456")

        # Use ADMIN (valid enum value) and password_hash (actual column name)
        await conn.execute(text("""
            INSERT INTO users (id, email, full_name, password_hash, hashed_password, role, is_active, is_verified, created_at, updated_at)
            VALUES (:id, :email, :full_name, :pw, :pw, CAST(:role AS user_role), :active, :verified, NOW(), NOW())
        """), {
            "id": uid,
            "email": "admin@compliance.ai",
            "full_name": "System Admin",
            "pw": hpw,
            "role": "ADMIN",
            "active": True,
            "verified": True,
        })
        print("Admin created: admin@compliance.ai / Admin@123456 (role=ADMIN)")

    await engine.dispose()

asyncio.run(seed())
