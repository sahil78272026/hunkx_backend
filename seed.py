import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.database import engine
from app.models.product import Product

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def seed():
    async with AsyncSessionLocal() as session:
        # delete all existing products
        await session.execute(text("DELETE FROM products"))
        
        products = [
            Product(name="Earth-Tone Smart Casual Fit", category="Smart Casual", price=2499, description="Fitted brown tee styled with beige tailored trousers.", images=["https://rlrcugmcgkbuhridzryj.supabase.co/storage/v1/object/public/hunkx_storage_sb/products/mens-smart-brown.jpeg"], sizes=["S", "M", "L", "XL"], stock=50),
            Product(name="Retro Athletic Streetwear", category="Vintage", price=2199, description="Red & black graphic tee paired with oversized vintage denim.", images=["https://rlrcugmcgkbuhridzryj.supabase.co/storage/v1/object/public/hunkx_storage_sb/products/mens-sports-red.jpeg"], sizes=["S", "M", "L", "XL"], stock=50),
            Product(name="Burgundy Elegance Fit", category="Smart Casual", price=2499, description="Fitted burgundy tee for that elevated everyday look.", images=["https://rlrcugmcgkbuhridzryj.supabase.co/storage/v1/object/public/hunkx_storage_sb/products/mens-smart-burgundy.jpeg"], sizes=["S", "M", "L", "XL"], stock=50),
            Product(name="Vibrant '08 Flying' Jersey", category="Trending", price=1899, description="Bold purple athletic streetwear paired with distressed denim.", images=["https://rlrcugmcgkbuhridzryj.supabase.co/storage/v1/object/public/hunkx_storage_sb/products/womens-sports-purple.jpeg"], sizes=["S", "M", "L", "XL"], stock=50),
            Product(name="'88' Flame Graphic Jersey", category="Street", price=1999, description="Turn up the heat with oversized edgy black streetwear.", images=["https://rlrcugmcgkbuhridzryj.supabase.co/storage/v1/object/public/hunkx_storage_sb/products/womens-streetwear-black.jpeg"], sizes=["S", "M", "L", "XL"], stock=50),
            Product(name="Utility Crop & Camo Fit", category="Utility", price=2899, description="Olive brown long-sleeve crop top with relaxed cargo pants.", images=["https://rlrcugmcgkbuhridzryj.supabase.co/storage/v1/object/public/hunkx_storage_sb/products/womens-utility-camo.jpeg"], sizes=["S", "M", "L", "XL"], stock=50),
            Product(name="'22' Star Pattern Jersey", category="Street", price=1899, description="White and navy oversized jersey for chic urban vibes.", images=["https://rlrcugmcgkbuhridzryj.supabase.co/storage/v1/object/public/hunkx_storage_sb/products/womens-streetwear-white.jpeg"], sizes=["S", "M", "L", "XL"], stock=50),
        ]
        
        session.add_all(products)
        await session.commit()
        print("Products seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed())
