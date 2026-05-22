import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.database import engine

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def clear_data():
    async with AsyncSessionLocal() as session:
        try:
            # Delete in order to respect foreign key constraints
            print("Deleting order events...")
            await session.execute(text("DELETE FROM order_events"))
            
            print("Deleting orders...")
            await session.execute(text("DELETE FROM orders"))
            
            print("Deleting addresses...")
            await session.execute(text("DELETE FROM addresses"))
            
            await session.commit()
            print("Database cleared successfully!")
        except Exception as e:
            await session.rollback()
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(clear_data())
