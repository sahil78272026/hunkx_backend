import resend
from typing import Any
from app.core.config import settings

# Use the Pydantic settings which automatically loads from .env
resend.api_key = settings.RESEND_API_KEY

class EmailService:
    def send_order_confirmation(self, order: Any):
        if not order.customer_email:
            print(f"No email provided for order {order.id}. Skipping email confirmation.")
            return

        if not resend.api_key:
            print(f"⚠️ RESEND_API_KEY is not set. Mocking email send to {order.customer_email}")
            return

        # Prepare email content
        items_html = "".join([
            f"<li>{item['quantity']}x {item['name']} ({item['size']}) - ₹{item['price']}</li>"
            for item in order.items
        ])
        
        html_content = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #111;">
            <div style="background: #000; padding: 20px; text-align: center;">
                <h1 style="color: #d4a23a; margin: 0; font-family: 'Times New Roman', serif;">HUNKX</h1>
            </div>
            <div style="padding: 20px; border: 1px solid #eee;">
                <h2>Order Confirmed!</h2>
                <p>Hi {order.customer_name},</p>
                <p>Thank you for shopping with Hunkx Apparel. Your order has been successfully placed and paid.</p>
                <p><strong>Order ID:</strong> {order.id}</p>
                <p><strong>Total Amount:</strong> ₹{order.total_amount}</p>
                
                <h3>Items Ordered:</h3>
                <ul>
                    {items_html}
                </ul>
                
                <p>We will notify you once your order is shipped!</p>
                <br/>
                <p>Stay Sharp,</p>
                <p><strong>The HUNKX Team</strong></p>
            </div>
        </div>
        """

        try:
            # Note: For Resend free tier without a custom domain, use 'onboarding@resend.dev' 
            # and you can only send emails to the exact email address you registered Resend with.
            r = resend.Emails.send({
                "from": "Hunkx Orders <onboarding@resend.dev>",
                "to": order.customer_email,
                "subject": f"HUNKX Order Confirmation - #{order.id[-6:].upper()}",
                "html": html_content
            })
            print(f"✅ Order confirmation email sent to {order.customer_email}")
            return r
        except Exception as e:
            print(f"❌ Failed to send email to {order.customer_email}: {e}")

email_service = EmailService()
