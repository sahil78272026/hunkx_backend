from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class OrderEvent(Base):
    """
    Audit log for tracking exactly what happens to an order and when.
    Useful for the Admin Control Room to see a timeline of the order.
    """
    __tablename__ = "order_events"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    order_id = Column(String, index=True, nullable=False) 
    event_type = Column(String, nullable=False) # e.g., "CREATED", "STATUS_CHANGED", "REFUNDED"
    payload = Column(JSON, nullable=True) # Any extra data (old status, new status, razorpay ids)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
