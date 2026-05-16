from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductResponseSchema, ProductCreateSchema
from app.core.security import get_admin_user

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)

@router.get("/", response_model=List[ProductResponseSchema])
async def get_all_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.active == True))
    products = result.scalars().all()
    return products

@router.get("/{product_id}", response_model=ProductResponseSchema)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id, Product.active == True))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreateSchema, 
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

@router.put("/{product_id}", response_model=ProductResponseSchema)
async def update_product(
    product_id: str,
    product_data: __import__('app.schemas.product', fromlist=['ProductUpdateSchema']).ProductUpdateSchema,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
        
    await db.commit()
    await db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Instead of hard delete, we can soft delete by setting active to False, or hard delete. Let's hard delete to free space.
    await db.delete(product)
    await db.commit()
    return None
