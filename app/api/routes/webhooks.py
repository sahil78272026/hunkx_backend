from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.order import Order
from app.models.product import Product
import json

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)

@router.post("/razorpay")
async def razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Razorpay calls this endpoint automatically when a payment succeeds.
    It updates the order status to PAID and decrements the product stock.
    """
    # 1. In a production app, we would verify the 'x-razorpay-signature' header here 
    # to ensure the request actually came from Razorpay.
    
    try:
        body = await request.body()
        payload = json.loads(body)
        event = payload.get("event")
        
        if event in ["payment.captured", "payment.authorized"]:
            payment_entity = payload["payload"]["payment"]["entity"]
            razorpay_order_id = payment_entity.get("order_id")
            
            if razorpay_order_id:
                # 2. Find the order in our database (lock it to prevent race conditions)
                result = await db.execute(
                    select(Order).where(Order.razorpay_order_id == razorpay_order_id).with_for_update()
                )
                order = result.scalar_one_or_none()
                
                # 3. If order exists and isn't already paid (Idempotency)
                if order and order.status != "PAID":
                    # Mark as PAID
                    order.status = "PAID"
                    order.razorpay_payment_id = payment_entity.get("id")
                    
                    # 4. Decrement Stock Logic
                    # We loop through the items bought and reduce their stock in the products table
                    for item in order.items:
                        product_id = item.get("id")
                        quantity_bought = item.get("quantity", 1)
                        
                        prod_result = await db.execute(select(Product).where(Product.id == product_id))
                        product = prod_result.scalar_one_or_none()
                        
                        if product and product.stock >= quantity_bought:
                            product.stock -= quantity_bought
                    
                    # Save changes
                    await db.commit()
                    print(f"✅ Order {order.id} marked as PAID and stock decremented.")
                    
                    # 5. Send Email Confirmation
                    from app.services.email_service import email_service
                    email_service.send_order_confirmation(order)
                    
        return {"status": "success"}
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        # We always return 200 OK to Razorpay so it doesn't keep retrying unnecessarily,
        # unless it's a critical server error.
        return {"status": "failed", "detail": str(e)}
