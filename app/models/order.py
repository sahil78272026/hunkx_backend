from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    customer_name = Column(String, nullable=False)
    customer_mobile = Column(String, nullable=False)
    customer_address = Column(String, nullable=False)
    customer_pincode = Column(String, nullable=False)
    
    total_amount = Column(Integer, nullable=False) # In rupees
    items = Column(JSON, nullable=False) # Array of items ordered
    
    # State Machine for the order flow
    status = Column(String, default="CREATED", nullable=False) # CREATED, PAID, PACKED, SHIPPED, DELIVERED
    
    # Razorpay tracking
    razorpay_order_id = Column(String, unique=True, index=True, nullable=True)
    razorpay_payment_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
