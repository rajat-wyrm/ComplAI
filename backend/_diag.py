import asyncio, os, sys, time, subprocess
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

G,R,Y,W = "\033[32m","\033[31m","\033[33m","\033[0m"
SEP = "="*55
results = []

def ok(label, detail=""):
    print(f"  {G}PASS{W}  {label}" + (f" | {detail[:70]}" if detail else ""))
    results.append(("PASS", label, ""))

def fail(label, detail=""):
    print(f"  {R}FAIL{W}  {label}" + (f" | {detail[:70]}" if detail else ""))
    results.append(("FAIL", label, detail))

def chk(label, fn):
    try:
        r = fn(); ok(label, str(r)[:60] if r else ""); return True
    except Exception as e:
        fail(label, str(e)[:80]); return False

async def achk(label, coro):
    try:
        r = await coro; ok(label, str(r)[:60] if r else ""); return True
    except Exception as e:
        fail(label, str(e)[:80]); return False

async def main():
    print("\n" + SEP)
    print("  AI Compliance Copilot - Full System Diagnostic")
    print(SEP + "\n")

    print("── Environment Variables ──")
    for k in ["DATABASE_URL","REDIS_URL","DEEPSEEK_API_KEY","OPENAI_API_KEY","SECRET_KEY","ENVIRONMENT"]:
        v = os.environ.get(k, "")
        m = (v[:4]+"****"+v[-4:]) if len(v) > 8 else ("SET" if v else "MISSING")
        col = G if v else R
        sym = "OK" if v else "XX"
        print(f"  {col}{sym}{W}  {k} = {m}")

    print("\n── Core Imports ──")
    for m in ["fastapi","sqlalchemy","asyncpg","jose","passlib","pydantic",
              "slowapi","cachetools","structlog","aiofiles",
              "app.models.database","app.models.user","app.models.token",
              "app.core.auth","app.core.cache","app.core.errors","app.core.database",
              "app.middleware.security","app.middleware.rate_limit",
              "app.api.routes.auth","app.api.routes.health","app.api.routes.analyze"]:
        chk(m, lambda m=m: __import__(m))

    print("\n── Database ──")
    async def db_ver():
        from app.models.database import ASYNC_URL
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        e = create_async_engine(ASYNC_URL, connect_args={"ssl": True})
        async with e.connect() as c:
            r = await c.execute(text("SELECT version()"))
            v = r.fetchone()[0][:45]
        await e.dispose()
        return v
    await achk("PostgreSQL connect", db_ver())

    async def db_tbl():
        from app.models.database import ASYNC_URL, Base
        import app.models.user, app.models.token
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        e = create_async_engine(ASYNC_URL, connect_args={"ssl": True})
        async with e.begin() as c:
            await c.run_sync(Base.metadata.create_all)
        async with e.connect() as c:
            r = await c.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' ORDER BY table_name"
            ))
            tables = [x[0] for x in r.fetchall()]
        await e.dispose()
        return str(tables)
    await achk("DB tables (create_all)", db_tbl())

    print("\n── Auth System ──")
    def auth_t():
        from app.core.auth import hash_password, verify_password, create_access_token, decode_access_token
        h = hash_password("TestPass123!")
        assert verify_password("TestPass123!", h)
        tok = create_access_token({"sub": "uid-1", "email": "t@t.com", "role": "ANALYST"})
        payload = decode_access_token(tok)
        assert payload["sub"] == "uid-1"
        return "bcrypt+JWT OK"
    chk("JWT + bcrypt", auth_t)

    print("\n── Cache ──")
    async def cache_t():
        from app.core.cache import cache_set, cache_get, cache_delete, get_cache_stats
        await cache_set("_t", "hello", ttl=30)
        v = await cache_get("_t")
        assert v == "hello", f"got: {v}"
        await cache_delete("_t")
        s = get_cache_stats()
        return "LRU=" + str(s["memory_size"]) + " redis=" + str(s["redis"])
    await achk("Two-tier cache", cache_t())

    print("\n── Seed Data ──")
    async def admin_t():
        from app.models.database import ASYNC_URL
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import select
        from app.models.user import User
        e = create_async_engine(ASYNC_URL, connect_args={"ssl": True})
        S = sessionmaker(e, class_=AsyncSession, expire_on_commit=False)
        async with S() as db:
            r = await db.execute(select(User).where(User.email == "admin@compliance.ai"))
            u = r.scalar_one_or_none()
        await e.dispose()
        assert u, "Admin not found in DB"
        return u.email + " role=" + str(u.role)
    await achk("Admin user in DB", admin_t())

    print("\n── Python Syntax Check ──")
    base = Path(__file__).parent
    so = sf = 0
    for f in sorted(base.rglob("app/**/*.py")):
        r = subprocess.run([sys.executable, "-m", "py_compile", str(f)], capture_output=True, text=True)
        rel = str(f.relative_to(base))
        if r.returncode != 0:
            sf += 1
            fail("syntax:" + rel, r.stderr.strip()[:80])
        else:
            so += 1
    col = G if sf == 0 else Y
    print(f"  {col}Syntax:{W} {so} files OK, {sf} errors")

    print("\n── HTTP Endpoints (server must be running) ──")
    try:
        import urllib.request, json
        urls = [
            "http://localhost:8000/",
            "http://localhost:8000/api/health",
            "http://localhost:8000/api/health/ready",
            "http://localhost:8000/api/health/full",
            "http://localhost:8000/docs",
        ]
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=3) as resp:
                    status = resp.status
                    col = G if status == 200 else Y
                    print(f"  {col}HTTP {status}{W}  {url}")
            except Exception as e:
                print(f"  {R}OFFLINE{W}  {url} - {str(e)[:40]}")
    except Exception as e:
        print(f"  {Y}HTTP check skipped:{W} {e}")

    print("\n" + SEP)
    passed = [x for x in results if x[0] == "PASS"]
    failed = [x for x in results if x[0] == "FAIL"]
    total = len(results)
    print(f"  TOTAL  : {total}")
    print(f"  {G}PASSED : {len(passed)}{W}")
    if failed:
        print(f"  {R}FAILED : {len(failed)}{W}")
        print("\n  Failed checks:")
        for x in failed:
            detail = x[2] if len(x) > 2 else ""
            print(f"    {R}FAIL{W}  {x[1]}" + (f" | {detail[:60]}" if detail else ""))
    else:
        print(f"  {G}ALL CHECKS PASSED - System fully healthy!{W}")
    print("")
    print(f"  Admin: admin@compliance.ai / Admin@123456")
    print(f"  Docs:  http://localhost:8000/docs")
    print(f"  App:   http://localhost:3001")
    print(SEP + "\n")

asyncio.run(main())
