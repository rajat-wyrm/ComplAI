import asyncio
from app.models.database import init_db
asyncio.run(init_db())
print("Tables created")
