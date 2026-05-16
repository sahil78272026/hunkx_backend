import asyncio
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
from app.core.database import AsyncSessionLocal
from app.models.order import Order
from app.models.product import Product
from app.services.payment_service import payment_service
from app.services.email_service import email_service
import logging

logger = logging.getLogger(__name__)

async def run_reconciliation_pass():
    """Single pass of the reconciliation logic. Extracted for easy testing."""
    try:
        logger.info("Running reconciliation cron job...")
        async with AsyncSessionLocal() as db:
            # For testing purposes, we'll check any order older than 1 minute (instead of 15)
            threshold_time = datetime.now(timezone.utc) - timedelta(minutes=1)
            one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
            
            result = await db.execute(
                select(Order).where(
                    (Order.status == "CREATED") &
                    (Order.created_at <= threshold_time) &
                    (Order.created_at >= one_day_ago) &
                    (Order.razorpay_order_id.isnot(None))
                )
            )
            pending_orders = result.scalars().all()
            
            if pending_orders:
                logger.info(f"Reconciliation: Found {len(pending_orders)} pending orders to check.")
            
            for order in pending_orders:
                try:
                    rzp_order = payment_service.fetch_order(order.razorpay_order_id)
                    
                    if rzp_order.get("status") == "paid":
                        logger.info(f"⚠️ RECONCILIATION FIX: Order {order.id} was paid! Webhook missed it. Fixing now.")
                        
                        lock_result = await db.execute(
                            select(Order).where(Order.id == order.id).with_for_update()
                        )
                        locked_order = lock_result.scalar_one()
                        
                        if locked_order.status != "PAID":
                            locked_order.status = "PAID"
                            
                            history = list(locked_order.status_history) if locked_order.status_history else []
                            history.append({"status": "PAID", "timestamp": datetime.now(timezone.utc).isoformat()})
                            locked_order.status_history = history
                            
                            for item in locked_order.items:
                                product_id = item.get("id")
                                quantity_bought = item.get("quantity", 1)
                                prod_result = await db.execute(select(Product).where(Product.id == product_id))
                                product = prod_result.scalar_one_or_none()
                                if product and product.stock >= quantity_bought:
                                    product.stock -= quantity_bought
                                    
                            await db.commit()
                            email_service.send_order_confirmation(locked_order)
                except Exception as e:
                    logger.error(f"Reconciliation error for order {order.id}: {e}")
            
    except Exception as e:
        logger.error(f"Reconciliation job failed: {e}")

async def reconcile_pending_orders():
    """Infinite loop for the background task."""
    await asyncio.sleep(5) 
    while True:
        await run_reconciliation_pass()
        await asyncio.sleep(60) # Sleep 60 seconds for easier testing right now
