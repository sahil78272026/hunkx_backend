import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def alter_table():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        from sqlalchemy import text
        print("Altering products table to change stock column to JSON...")
        await conn.execute(text("ALTER TABLE products ALTER COLUMN stock TYPE JSON USING concat('{\"S\": ', stock, '}')::json;"))
        print("Successfully altered column type!")

if __name__ == "__main__":
    asyncio.run(alter_table())
