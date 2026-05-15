import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

async def migrate():
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE orders ADD COLUMN user_id VARCHAR;"))
            print("Successfully added user_id column.")
        except Exception as e:
            print("Error or already exists:", e)

asyncio.run(migrate())
