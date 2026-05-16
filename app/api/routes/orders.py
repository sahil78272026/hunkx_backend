from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.order import Order
from app.schemas.order import OrderCreateSchema, OrderResponseSchema
from app.services.payment_service import payment_service

from app.core.security import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["Orders"], # Groups this endpoint under 'Orders' in Swagger UI
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=OrderResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreateSchema, 
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    Create a new order in the system and generate a secure Razorpay Order.
    Requires a logged-in user.
    """
    try:
        # 1. Create the Database Order first
        new_order = Order(
            customer_name=order_data.customer_name,
            customer_email=order_data.customer_email,
            customer_mobile=order_data.customer_mobile,
            customer_address=order_data.customer_address,
            customer_pincode=order_data.customer_pincode,
            total_amount=order_data.total_amount,
            items=[item.model_dump() for item in order_data.items],
            status="CREATED",
            status_history=[{"status": "CREATED", "timestamp": datetime.now(timezone.utc).isoformat()}],
            user_id=user.id
        )
        db.add(new_order)
        # Flush to generate our internal order ID without committing the transaction yet
        await db.flush() 

        # 2. Securely create the Razorpay Order
        rzp_order = payment_service.create_order(
            amount_in_rupees=new_order.total_amount,
            receipt_id=new_order.id
        )

        # 3. Save the Razorpay Order ID to our database record
        new_order.razorpay_order_id = rzp_order.get("id")
        
        # 4. Commit everything
        await db.commit()
        await db.refresh(new_order)
        
        return new_order
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@router.get("/my-orders", response_model=List[OrderResponseSchema])
async def get_my_orders(db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    """
    Fetch all orders placed by the currently logged-in user.
    """
    from sqlalchemy.future import select
    result = await db.execute(select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc()))
    orders = result.scalars().all()
    return orders

@router.get("/{order_id}", response_model=OrderResponseSchema)
async def get_order_status(order_id: str, db: AsyncSession = Depends(get_db)):
    """
    Fetch an order's status by its internal ID. Used by the Tracking page.
    """
    from sqlalchemy.future import select
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    return order
