import asyncio
from app.core.database import engine, Base
from app.models.address import Address

async def init_models():
    async with engine.begin() as conn:
        print("Creating Address table...")
        await conn.run_sync(Base.metadata.create_all)
        print("Done!")

if __name__ == "__main__":
    asyncio.run(init_models())
