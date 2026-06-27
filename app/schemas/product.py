from pydantic import BaseModel
from typing import List, Optional, Dict

class ProductBaseSchema(BaseModel):
    name: str
    category: str
    price: int
    description: Optional[str] = None
    images: List[str]
    sizes: List[str]
    stock: Dict[str, int] = {}
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
    stock: Optional[Dict[str, int]] = None
    active: Optional[bool] = None

class ProductResponseSchema(ProductBaseSchema):
    id: str

    class Config:
        from_attributes = True
