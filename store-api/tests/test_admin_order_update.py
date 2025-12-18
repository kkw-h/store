import pytest
import uuid
from app.models.order import Order, OrderItem
from app.models.user import User
from app.core.config import settings

@pytest.mark.asyncio
async def test_update_order_items(client, db_session, admin_token_headers):
    # 1. Setup Data
    # Create User
    unique_suffix = str(uuid.uuid4())[:8]
    user = User(openid=f"test_user_{unique_suffix}", nickname="Test User")
    db_session.add(user)
    await db_session.flush()
    
    # Create Order
    order = Order(
        order_no=f"TEST_UPDATE_{unique_suffix}",
        user_id=user.id,
        total_amount=100.00,
        delivery_fee=10.00,
        final_amount=110.00,
        status=1,
        delivery_type="delivery",
        address_snapshot={}
    )
    db_session.add(order)
    await db_session.flush()
    
    # Create Items
    item1 = OrderItem(
        order_id=order.id,
        product_name="Product A",
        price=30.00,
        quantity=2 # 60.00
    )
    item2 = OrderItem(
        order_id=order.id,
        product_name="Product B",
        price=40.00,
        quantity=1 # 40.00
    )
    db_session.add(item1)
    db_session.add(item2)
    await db_session.commit()
    await db_session.refresh(item1)
    await db_session.refresh(item2)
    await db_session.refresh(order)
    
    # Initial Check
    assert order.total_amount == 100.00
    
    # 2. Update Items
    # Change Item 1 quantity to 1 (30.00)
    # Remove Item 2 (0.00)
    payload = {
        "order_id": order.id,
        "items": [
            {
                "item_id": item1.id,
                "quantity": 1
            },
            {
                "item_id": item2.id,
                "is_removed": True
            }
        ]
    }
    
    response = await client.post(
        f"{settings.API_V1_STR}/admin/order/update_items",
        headers=admin_token_headers,
        json=payload
    )
    
    assert response.status_code == 200, response.text
    
    # 3. Verify
    await db_session.refresh(order)
    await db_session.refresh(item1)
    await db_session.refresh(item2)
    
    # Item 1: Qty 1
    assert item1.quantity == 1
    assert item1.is_removed == False
    
    # Item 2: Removed
    assert item2.is_removed == True
    
    # Calc:
    # Item 1: 30 * 1 = 30
    # Item 2: Removed = 0
    # Total = 30
    # Final = 30 + 10 = 40
    
    assert float(order.total_amount) == 30.00
    assert float(order.final_amount) == 40.00
