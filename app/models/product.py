from sqlalchemy import Column, String, Integer, Boolean, JSON
from app.core.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Integer, nullable=False) # In rupees
    description = Column(String, nullable=True)
    
    # Store arrays as JSON (e.g. ["url1", "url2"])
    images = Column(JSON, nullable=False, default=list) 
    
    # Available sizes (e.g. ["S", "M", "L", "XL"])
    sizes = Column(JSON, nullable=False, default=list)
    
    # Total stock across all sizes (for MVP) or we could make it a dict per size
    stock = Column(Integer, default=0, nullable=False)
    
    # Is the product visible on the website?
    active = Column(Boolean, default=True, nullable=False)
