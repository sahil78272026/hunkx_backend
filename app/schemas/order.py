from pydantic import BaseModel
from typing import List, Optional

class OrderItemSchema(BaseModel):
    id: str
    name: str
    size: str
    price: int
    quantity: int

class OrderCreateSchema(BaseModel):
    customer_name: str
    customer_mobile: str
    customer_address: str
    customer_pincode: str
    items: List[OrderItemSchema]
    total_amount: int

class OrderResponseSchema(BaseModel):
    id: str
    status: str
    razorpay_order_id: Optional[str] = None
    total_amount: int

    class Config:
        from_attributes = True
