import asyncio
from app.core.database import engine, Base
from app.models.order import Order
from app.models.product import Product # Import all models here so Base knows about them

async def init_models():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("Successfully created database tables in Supabase!")

if __name__ == "__main__":
    asyncio.run(init_models())
