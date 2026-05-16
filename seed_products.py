import asyncio
import sys
import os

# Add backend directory to sys.path so we can import app modules directly when running this script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base, AsyncSessionLocal
from app.models.product import Product

async def seed():
    print("Creating tables if they do not exist...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    products = [
      {
        "id": "1",
        "name": "Acid Wash Signature Tee",
        "category": "Acid Wash",
        "price": 1499,
        "description": "Bleached. Rugged. Unapologetic. Our signature heavy-weight cotton tee.",
        "images": ["https://placehold.co/400x500/16110a/d4a23a?text=Acid+Wash+Tee"],
        "sizes": ["S", "M", "L", "XL"],
        "stock": 100
      },
      {
        "id": "2",
        "name": "Street Classic Jeans",
        "category": "Street",
        "price": 2499,
        "description": "Built for the daily flex. Baggy fit, premium denim.",
        "images": ["https://placehold.co/400x500/16110a/d4a23a?text=Street+Jeans"],
        "sizes": ["28", "30", "32", "34"],
        "stock": 100
      },
      {
        "id": "3",
        "name": "'26 Edit Hoodie",
        "category": "New Year",
        "price": 2999,
        "description": "A fresh start, sharply dressed. Limited edition 2026 drop.",
        "images": ["https://placehold.co/400x500/16110a/d4a23a?text=26+Edit+Hoodie"],
        "sizes": ["M", "L", "XL"],
        "stock": 50
      },
      {
        "id": "4",
        "name": "Gold Skull Oversized",
        "category": "Signature",
        "price": 1899,
        "description": "Oversized fit with subtle gold foil skull print on the back.",
        "images": ["https://placehold.co/400x500/16110a/d4a23a?text=Gold+Skull"],
        "sizes": ["S", "M", "L"],
        "stock": 200
      }
    ]
    
    async with AsyncSessionLocal() as db:
        for p_data in products:
            existing = await db.get(Product, p_data["id"])
            if not existing:
                p = Product(**p_data)
                db.add(p)
                print(f"Added product: {p.name}")
            else:
                print(f"Product {existing.name} already exists.")
        await db.commit()
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed())
