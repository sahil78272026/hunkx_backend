import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.models.order import Order
from app.core.cron import run_reconciliation_pass

@pytest.mark.asyncio
async def test_reconciliation_pass_marks_paid():
    """
    Test that the reconciliation logic correctly identifies a 'CREATED' order
    that was paid in Razorpay, updates its status to 'PAID', and sends an email.
    """
    # 1. Mock the Database Session
    mock_db = MagicMock()
    mock_order = Order(
        id="test-order-123",
        status="CREATED",
        razorpay_order_id="order_rzp_mock",
        items=[{"id": "prod_1", "quantity": 1}]
    )
    
    # 2. Mock Razorpay's API response
    mock_rzp_response = {"status": "paid"}
    
    with patch("app.core.cron.AsyncSessionLocal") as mock_session_maker:
        with patch("app.core.cron.payment_service.fetch_order", return_value=mock_rzp_response) as mock_fetch:
            with patch("app.core.cron.email_service.send_order_confirmation") as mock_email:
                
                # Setup DB mocks to return our fake order
                mock_session_ctx = mock_session_maker.return_value.__aenter__.return_value
                
                # Mock first query (finding pending orders)
                mock_result1 = MagicMock()
                mock_result1.scalars.return_value.all.return_value = [mock_order]
                
                # Mock second query (locking the order)
                mock_result2 = MagicMock()
                mock_result2.scalar_one.return_value = mock_order

                # Mock third query (fetching product for stock decrement)
                mock_result3 = MagicMock()
                mock_result3.scalar_one_or_none.return_value = None # product not found or ignore for test
                
                # Have execute() return result1 then result2 then result3
                mock_session_ctx.execute.side_effect = [mock_result1, mock_result2, mock_result3]
                
                # 3. Run the function
                await run_reconciliation_pass()
                
                # 4. Assertions
                mock_fetch.assert_called_once_with("order_rzp_mock")
                assert mock_order.status == "PAID"
                mock_email.assert_called_once_with(mock_order)
                print("✅ Test Passed: Reconciliation logic successfully fixed the stuck order!")

