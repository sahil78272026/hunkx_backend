from pydantic import BaseModel
from typing import List, Optional

class ProductBaseSchema(BaseModel):
    name: str
    category: str
    price: int
    description: Optional[str] = None
    images: List[str]
    sizes: List[str]
    stock: int = 0
    active: bool = True

class ProductCreateSchema(ProductBaseSchema):
    pass

class ProductUpdateSchema(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None
    sizes: Optional[List[str]] = None
    stock: Optional[int] = None
    active: Optional[bool] = None

class ProductResponseSchema(ProductBaseSchema):
    id: str

    class Config:
        from_attributes = True
