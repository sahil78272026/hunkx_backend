from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.order import Order
from app.core.security import get_admin_user
from datetime import datetime, timedelta, timezone
from collections import defaultdict

router = APIRouter(
    prefix="/admin/analytics",
    tags=["Admin Analytics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_analytics(db: AsyncSession = Depends(get_db), admin_user = Depends(get_admin_user)):
    result = await db.execute(select(Order))
    orders = result.scalars().all()
    
    # 1. KPIs
    valid_statuses = ["PAID", "PACKED", "SHIPPED", "DELIVERED"]
    valid_orders = [o for o in orders if o.status in valid_statuses]
    
    gross_revenue = sum(o.total_amount for o in valid_orders)
    total_valid_orders = len(valid_orders)
    aov = round(gross_revenue / total_valid_orders, 2) if total_valid_orders > 0 else 0
    
    total_units_sold = 0
    for o in valid_orders:
        for item in o.items:
            total_units_sold += item.get("quantity", 1)
            
    # 2. Funnel
    funnel = {
        "checkout_initiated": len(orders),
        "payment_success": total_valid_orders,
        "shipped_or_delivered": len([o for o in orders if o.status in ["SHIPPED", "DELIVERED"]]),
        "refunded_or_cancelled": len([o for o in orders if o.status in ["REFUNDED", "CANCELLED"]])
    }
    
    # 3. Top Products
    product_stats = defaultdict(lambda: {"quantity": 0, "revenue": 0})
    for o in valid_orders:
        for item in o.items:
            name = item.get("name", "Unknown")
            qty = item.get("quantity", 1)
            price = item.get("price", 0)
            product_stats[name]["quantity"] += qty
            product_stats[name]["revenue"] += (qty * price)
            
    # Sort by quantity
    top_products = sorted(
        [{"name": k, **v} for k, v in product_stats.items()],
        key=lambda x: x["quantity"],
        reverse=True
    )[:5]
    
    # 4. 7-Day Revenue Trend
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=6)
    
    daily_revenue = { (today - timedelta(days=i)).strftime("%Y-%m-%d"): 0 for i in range(7) }
    
    for o in valid_orders:
        if o.created_at:
            order_date = o.created_at.date()
            if order_date >= seven_days_ago:
                date_str = order_date.strftime("%Y-%m-%d")
                if date_str in daily_revenue:
                    daily_revenue[date_str] += o.total_amount
                    
    trend_data = [{"date": k, "revenue": v} for k, v in sorted(daily_revenue.items())]
    
    return {
        "kpis": {
            "gross_revenue": gross_revenue,
            "aov": aov,
            "total_units_sold": total_units_sold
        },
        "funnel": funnel,
        "top_products": top_products,
        "trend_data": trend_data
    }
