from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Dict, Any
from app.core.database import get_db
from app.models.order import Order
from app.schemas.order import OrderResponseSchema
from app.core.security import get_admin_user
from pydantic import BaseModel

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)

class OrderStatusUpdate(BaseModel):
    status: str

@router.get("/orders", response_model=List[OrderResponseSchema])
async def get_all_orders(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db), 
    admin_user = Depends(get_admin_user)
):
    """
    Fetch all platform orders (Admin only).
    """
    result = await db.execute(select(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit))
    orders = result.scalars().all()
    return orders

@router.put("/orders/{order_id}/status", response_model=OrderResponseSchema)
async def update_order_status(
    order_id: str, 
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db), 
    admin_user = Depends(get_admin_user)
):
    """
    Update the status of an order (Admin only).
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    from datetime import datetime, timezone
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.status = status_update.status
    
    # Append to status history
    history = list(order.status_history) if order.status_history else []
    history.append({"status": status_update.status, "timestamp": datetime.now(timezone.utc).isoformat()})
    
    # SQLAlchemy requires assigning a new object/list for JSON column updates to be detected
    order.status_history = history
    
    await db.commit()
    await db.refresh(order)
    return order

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db), 
    admin_user = Depends(get_admin_user)
):
    """
    Get key metrics for the admin dashboard: total revenue, order count, pending orders.
    """
    # Total Revenue (only from PAID or successful orders, here we assume all orders in DB are valid or we can filter by status)
    result_revenue = await db.execute(select(func.sum(Order.total_amount)).where(Order.status != "CREATED"))
    total_revenue = result_revenue.scalar() or 0
    
    # Total Orders
    result_orders = await db.execute(select(func.count(Order.id)))
    total_orders = result_orders.scalar() or 0
    
    # Pending Orders (e.g. status == "PAID" which means paid but not shipped)
    result_pending = await db.execute(select(func.count(Order.id)).where(Order.status == "PAID"))
    pending_orders = result_pending.scalar() or 0

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "pending_orders": pending_orders
    }
