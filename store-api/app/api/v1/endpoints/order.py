from typing import List, Any
from datetime import datetime
import random
import time
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.user import User, UserAddress
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderTimeline
from app.schemas import order as order_schemas
from app.schemas.response import ResponseModel, success

router = APIRouter()

# Helper to generate order no
def generate_order_no():
    return f"{time.strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"

# Helper to get status text
def get_status_text(status: int, delivery_type: str) -> str:
    status_map = {
        0: "待支付",
        1: "待接单",
        2: "待自提" if delivery_type == "pickup" else "待发货",
        3: "配送中",
        4: "已完成",
        -1: "已取消"
    }
    return status_map.get(status, "未知状态")

@router.post("/cancel", response_model=ResponseModel)
async def cancel_order(
    cancel_in: order_schemas.OrderCancelRequest,
    session: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    用户主动取消订单
    仅限: 待支付(0), 待接单(1), 待自提(2) 状态
    """
    query = select(Order).where(Order.id == cancel_in.order_id, Order.user_id == current_user.id)
    result = await session.execute(query)
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
        
    # Check status
    # Allow cancel if status is 0, 1, or 2 (before merchant accepts for delivery, or before pickup verified?)
    # Logic: 
    # - 0: Pending Payment -> OK
    # - 1: Pending Delivery (Merchant hasn't accepted yet) -> OK
    # - 2: Pending Pickup (Merchant hasn't verified yet) -> OK? Usually yes.
    if order.status not in [0, 1, 2]:
         raise HTTPException(status_code=400, detail="当前订单状态不可取消")
         
    order.status = -1
    order.reject_reason = f"用户主动取消: {cancel_in.reason or ''}"
    
    # Restore Stock? 
    # In a real system, we should restore stock.
    # For simplicity, we skip it or implement simple logic.
    # Let's restore stock.
    # We need to load items.
    # But wait, we didn't eager load items.
    
    # Re-fetch with items
    query_items = select(OrderItem).where(OrderItem.order_id == order.id)
    result_items = await session.execute(query_items)
    items = result_items.scalars().all()
    
    for item in items:
        # Find product
        prod = await session.get(Product, item.product_id)
        if prod:
            prod.stock += item.quantity
            prod.sales_count -= item.quantity
    
    # Add timeline
    timeline = OrderTimeline(
        order_id=order.id,
        status="已取消",
        remark="用户主动取消"
    )
    session.add(timeline)
    
    await session.commit()
    
    return success(msg="订单已取消")
@router.post("/preview", response_model=ResponseModel[order_schemas.OrderPreviewResponse])
async def preview_order(
    preview_in: order_schemas.OrderPreviewRequest,
    session: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    订单预检 (结算页)
    """
    # 1. Fetch products
    product_ids = [item.product_id for item in preview_in.items]
    result = await session.execute(select(Product).where(Product.id.in_(product_ids)))
    products = {p.id: p for p in result.scalars().all()}
    
    total_goods_price = Decimal(0)
    for item in preview_in.items:
        product = products.get(item.product_id)
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
        if product.status != 1:
            raise HTTPException(status_code=400, detail=f"Product {product.name} is off shelves")
        if product.stock < item.count:
             raise HTTPException(status_code=400, detail=f"Product {product.name} stock insufficient")
        
        total_goods_price += product.price * item.count
        
    # 2. Calculate Delivery Fee (Simple logic: 3.00 fee, free over 30.00)
    delivery_fee = Decimal("3.00") if preview_in.delivery_type == "delivery" and total_goods_price < 30 else Decimal("0.00")
    delivery_msg = "满30免运费" if preview_in.delivery_type == "delivery" else "自提免运费"
    
    final_price = total_goods_price + delivery_fee
    
    return success(data={
        "total_goods_price": total_goods_price,
        "delivery_fee": delivery_fee,
        "final_price": final_price,
        "is_open": True, # TODO: Check ShopConfig
        "delivery_msg": delivery_msg
    })

@router.post("/create", response_model=ResponseModel[order_schemas.OrderCreateResponse])
async def create_order(
    order_in: order_schemas.OrderCreateRequest,
    session: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    创建订单
    """
    # 1. Validate Items & Stock
    product_ids = [item.product_id for item in order_in.items]
    result = await session.execute(select(Product).where(Product.id.in_(product_ids)))
    products = {p.id: p for p in result.scalars().all()}
    
    total_goods_price = Decimal(0)
    order_items = []
    
    for item in order_in.items:
        product = products.get(item.product_id)
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
        if product.stock < item.count:
             raise HTTPException(status_code=400, detail=f"Product {product.name} stock insufficient")
        
        # Deduct stock (Simple version, optimistic lock needed in prod)
        product.stock -= item.count
        product.sales_count += item.count
        
        total_goods_price += product.price * item.count
        
        # Create OrderItem snapshot
        order_items.append(OrderItem(
            product_id=product.id,
            product_name=product.name,
            product_image=product.thumb_url,
            price=product.price,
            quantity=item.count
        ))

    # 2. Handle Delivery Info
    address_snapshot = None
    if order_in.delivery_type == "delivery":
        if not order_in.address_id:
             raise HTTPException(status_code=400, detail="Address ID required for delivery")
        address = await session.get(UserAddress, order_in.address_id)
        if not address or address.user_id != current_user.id:
             raise HTTPException(status_code=400, detail="Invalid address")
        
        address_snapshot = {
            "name": address.contact_name,
            "phone": address.contact_phone,
            "address": address.detail_address
        }
        
    delivery_fee = Decimal("3.00") if order_in.delivery_type == "delivery" and total_goods_price < 30 else Decimal("0.00")
    final_amount = total_goods_price + delivery_fee
    
    # 3. Create Order
    order_no = generate_order_no()
    pickup_code = str(random.randint(100000, 999999)) if order_in.delivery_type == "pickup" else None
    
    # Status: Skip payment for now -> Directly to PENDING_DELIVERY/PICKUP
    # In real world: Status = 0 (Pending Payment)
    initial_status = 1 if order_in.delivery_type == "delivery" else 2
    
    order = Order(
        order_no=order_no,
        user_id=current_user.id,
        total_amount=total_goods_price,
        delivery_fee=delivery_fee,
        final_amount=final_amount,
        status=initial_status, 
        delivery_type=order_in.delivery_type.value,
        address_snapshot=address_snapshot,
        pickup_code=pickup_code,
        pickup_time=order_in.pickup_time,
        remark=order_in.remark
    )
    session.add(order)
    await session.flush() # Get Order ID
    
    # Add Items
    for item in order_items:
        item.order_id = order.id
        session.add(item)
    
    # Add Timeline
    timeline_logs = [OrderTimeline(order_id=order.id, status="下单成功")]
    if initial_status > 0:
        # Mock payment success since we skip payment flow
        timeline_logs.append(OrderTimeline(order_id=order.id, status="支付成功", remark="Mock Payment"))
    
    for log in timeline_logs:
        session.add(log)
        
    await session.commit()
    await session.refresh(order)
    
    return success(data={
        "order_id": order.id,
        "order_no": order.order_no,
        "pay_params": {"mock": "pay_params"}
    })

@router.get("/list", response_model=ResponseModel[List[order_schemas.OrderListOut]])
async def list_orders(
    status: int = 0, # 0 for all
    session: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    订单列表
    """
    query = select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc())
    
    if status != 0:
        query = query.where(Order.status == status)
        
    # Eager load items for thumbnails
    query = query.options(selectinload(Order.items))
    
    result = await session.execute(query)
    orders = result.scalars().all()
    
    # Process status text
    order_list = []
    for o in orders:
        o.status_text = get_status_text(o.status, o.delivery_type)
        order_list.append(o)
        
    return success(data=order_list)

@router.get("/detail", response_model=ResponseModel[order_schemas.OrderDetailOut])
async def get_order_detail(
    order_id: int,
    session: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    订单详情 (含时间轴)
    """
    query = select(Order)\
        .where(Order.id == order_id, Order.user_id == current_user.id)\
        .options(selectinload(Order.items), selectinload(Order.timeline))
    
    result = await session.execute(query)
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.status_text = get_status_text(order.status, order.delivery_type)
    
    return success(data=order)
