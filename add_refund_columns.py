import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def add_columns():
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS refund_reason VARCHAR;"))
            await db.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS refund_rejection_reason VARCHAR;"))
            await db.commit()
            print("Added refund columns successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(add_columns())
