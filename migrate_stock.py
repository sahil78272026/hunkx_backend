import asyncio
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.product import Product
import json

async def run_migration():
    print("Starting stock migration...")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Product))
        products = result.scalars().all()
        
        migrated_count = 0
        for p in products:
            # SQLAlchemy might return it as int if it was stored as integer JSON
            if isinstance(p.stock, int) or isinstance(p.stock, str):
                try:
                    stock_val = int(p.stock)
                except ValueError:
                    stock_val = 0
                
                new_stock = {}
                sizes = p.sizes if isinstance(p.sizes, list) else []
                if sizes:
                    # Distribute stock evenly among sizes, or just assign total to first size
                    amount_per_size = stock_val // len(sizes) if len(sizes) > 0 else stock_val
                    for size in sizes:
                        new_stock[size] = amount_per_size
                
                p.stock = new_stock
                migrated_count += 1
                print(f"Migrated product {p.name} stock to {new_stock}")
                
        if migrated_count > 0:
            await db.commit()
            print(f"Successfully migrated {migrated_count} products!")
        else:
            print("No products needed migration.")

if __name__ == "__main__":
    asyncio.run(run_migration())
