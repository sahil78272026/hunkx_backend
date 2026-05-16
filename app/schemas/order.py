from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemSchema(BaseModel):
    id: str
    name: str
    size: str
    price: int
    quantity: int

class OrderCreateSchema(BaseModel):
    customer_name: str
    customer_email: str
    customer_mobile: str
    customer_address: str
    customer_pincode: str
    items: List[OrderItemSchema]
    total_amount: int

class OrderResponseSchema(BaseModel):
    id: str
    status: str
    status_history: List[dict] = []
    razorpay_order_id: Optional[str] = None
    total_amount: int
    items: List[OrderItemSchema]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
