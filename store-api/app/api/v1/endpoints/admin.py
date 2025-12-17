from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update, delete
from sqlalchemy.orm import selectinload
from typing import Any, List
from datetime import datetime, time

from app.api import deps
from app.models.order import Order, OrderTimeline, OrderItem
from app.models.shop import ShopConfig
from app.models.product import Product, Category
from app.models.user import User
from app.schemas import admin as admin_schemas, order as order_schemas, product as product_schemas, user as user_schemas
from app.schemas.response import ResponseModel, success

router = APIRouter()

@router.get("/order/list", response_model=ResponseModel[List[order_schemas.OrderListOut]])
async def list_all_orders(
    status: int = 0,
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    管理员获取订单列表
    """
    query = select(Order).order_by(Order.created_at.desc())
    
    if status != 0:
        query = query.where(Order.status == status)
        
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Paginate
    query = query.offset((page - 1) * size).limit(size)
    query = query.options(selectinload(Order.items))
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # Process status text
    from app.api.v1.endpoints.order import get_status_text
    order_list = []
    for o in orders:
        o.status_text = get_status_text(o.status, o.delivery_type)
        order_list.append(o)
        
    return success(data={
        "list": order_list,
        "total": total,
        "page": page,
        "size": size
    })

@router.get("/order/detail", response_model=ResponseModel[order_schemas.OrderDetailOut])
async def get_admin_order_detail(
    order_id: int,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    管理员获取订单详情
    """
    query = select(Order)\
        .where(Order.id == order_id)\
        .options(selectinload(Order.items), selectinload(Order.timeline))
    
    result = await db.execute(query)
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    from app.api.v1.endpoints.order import get_status_text
    order.status_text = get_status_text(order.status, order.delivery_type)
    
    return success(data=order)

@router.post("/order/audit", response_model=ResponseModel)
async def audit_order(
    request: admin_schemas.OrderAuditRequest,
    db: AsyncSession = Depends(deps.get_db),
    # current_user = Depends(deps.get_current_active_superuser) # TODO: Add admin permission check
) -> Any:
    """
    商家接单/拒单 (配送单)
    针对状态为 1 (待接单) 的配送订单。
    """
    # 查询订单
    result = await db.execute(select(Order).where(Order.id == request.order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order.status != 1:
        raise HTTPException(status_code=400, detail="当前订单状态不可操作")
    
    if request.action == "accept":
        order.status = 3  # 配送中
        timeline_remark = "商家已接单，准备配送"
        timeline_status = "商家已接单"
    elif request.action == "reject":
        if not request.reject_reason:
            raise HTTPException(status_code=400, detail="拒单原因必填")
        order.status = -1  # 已关闭/退款
        order.reject_reason = request.reject_reason
        timeline_remark = f"原因: {request.reject_reason}"
        timeline_status = "商家拒单"
    else:
        raise HTTPException(status_code=400, detail="无效的操作类型")
    
    # 添加时间轴
    timeline = OrderTimeline(
        order_id=order.id,
        status=timeline_status,
        remark=timeline_remark
    )
    db.add(timeline)
    
    await db.commit()
    await db.refresh(order)
    
    return success(msg="操作成功")

@router.post("/order/complete_delivery", response_model=ResponseModel)
async def complete_delivery(
    request: admin_schemas.CompleteDeliveryRequest,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    确认送达 (配送单)
    商家送完货后点击。
    """
    result = await db.execute(select(Order).where(Order.id == request.order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order.status != 3:
        raise HTTPException(status_code=400, detail="订单不是配送中状态")
    
    order.status = 4  # 已完成
    order.verified_at = func.now()
    
    timeline = OrderTimeline(
        order_id=order.id,
        status="订单已送达",
        remark="商家确认送达"
    )
    db.add(timeline)
    
    await db.commit()
    
    return success(msg="操作成功")

@router.post("/order/verify", response_model=ResponseModel)
async def verify_pickup(
    request: admin_schemas.VerifyPickupRequest,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    扫码核销 (自提单)
    商家扫描用户二维码或输入6位数字码。
    """
    # 查找订单
    result = await db.execute(select(Order).where(Order.pickup_code == request.code))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="无效的核销码")
    
    if order.status != 2:
        # 可能是已经核销过的，或者还没支付的
        if order.status == 4:
            raise HTTPException(status_code=400, detail="该订单已核销")
        raise HTTPException(status_code=400, detail="订单状态不满足核销条件")
        
    order.status = 4  # 已完成
    order.verified_at = func.now()
    
    # 保存ID供后续查询使用，防止commit后对象过期访问触发IO
    target_order_id = order.id
    
    timeline = OrderTimeline(
        order_id=order.id,
        status="自提核销完成",
        remark="商家扫码核销"
    )
    db.add(timeline)
    
    await db.commit()
    
    # 构建返回信息
    # 直接查询 OrderItem 表，避免 Relationship Lazy Load 问题
    from app.models.order import OrderItem
    
    # 重新查询订单信息 (commit后对象过期)
    result = await db.execute(select(Order).where(Order.id == target_order_id))
    order_loaded = result.scalar_one()
    
    # 查询订单项
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == target_order_id))
    items = result.scalars().all()
    
    items_data = []
    for item in items:
        items_data.append({
            "product_name": item.product_name,
            "quantity": item.quantity,
            "price": str(item.price)
        })
        
    order_info = {
        "order_no": order_loaded.order_no,
        "total_amount": str(order_loaded.final_amount),
        "items": items_data
    }

    return success(
        data={
            "success": True,
            "order_info": order_info
        }
    )

from sqlalchemy.orm import selectinload
from app.models.product import Product

@router.get("/dashboard", response_model=ResponseModel)
async def get_dashboard_stats(
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    数据看板
    """
    today = datetime.now().date()
    
    # Today Orders
    result = await db.execute(
        select(func.count(Order.id))
        .where(func.date(Order.created_at) == today)
    )
    today_orders = result.scalar_one()
    
    # Today Sales (Completed orders)
    result = await db.execute(
        select(func.sum(Order.final_amount))
        .where(func.date(Order.created_at) == today)
        .where(Order.status == 4)
    )
    today_sales = result.scalar_one() or 0
    
    # Pending Orders
    result = await db.execute(
        select(func.count(Order.id))
        .where(Order.status.in_([1, 2])) # Pending Delivery/Pickup
    )
    pending_orders = result.scalar_one()
    
    return success(data={
        "today_orders": today_orders,
        "today_sales": str(today_sales),
        "pending_orders": pending_orders
    })

@router.post("/product/stock", response_model=ResponseModel)
async def adjust_stock(
    product_id: int,
    stock: int,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    快速调整商品库存
    """
    product = await db.get(Product, product_id)
    if not product:
         raise HTTPException(status_code=404, detail="Product not found")
         
    product.stock = stock
    await db.commit()
    return success(msg="库存已更新")

@router.get("/shop/config", response_model=ResponseModel[admin_schemas.ShopConfigOut])
async def get_shop_config(
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    获取店铺配置
    """
    result = await db.execute(select(ShopConfig).limit(1))
    config = result.scalar_one_or_none()
    
    if not config:
        # Return default config
        return success(data={
            "is_open": True,
            "open_time": "09:00",
            "close_time": "22:00",
            "delivery_fee": 0.0,
            "min_order_amount": 0.0,
            "store_name": "社区优选",
            "store_address": "",
            "store_phone": ""
        })
    
    # Format times
    return success(data={
        "is_open": config.is_open,
        "open_time": config.open_time.strftime("%H:%M"),
        "close_time": config.close_time.strftime("%H:%M"),
        "delivery_fee": config.delivery_fee,
        "min_order_amount": config.min_order_amount,
        "store_name": config.store_name,
        "store_address": config.store_address,
        "store_phone": config.store_phone
    })

@router.post("/shop/config", response_model=ResponseModel)
async def update_shop_config(
    request: admin_schemas.ShopConfigUpdate,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    店铺状态设置
    """
    # 查询配置
    result = await db.execute(select(ShopConfig).limit(1))
    config = result.scalar_one_or_none()
    
    # 解析时间字符串
    try:
        open_t = datetime.strptime(request.open_time, "%H:%M").time()
        close_t = datetime.strptime(request.close_time, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="时间格式错误，应为 HH:MM")
        
    if not config:
        # 初始化
        config = ShopConfig(
            store_name=request.store_name,
            is_open=bool(request.is_open),
            open_time=open_t,
            close_time=close_t,
            delivery_fee=request.delivery_fee,
            min_order_amount=request.min_order_amount,
            store_address=request.store_address,
            store_phone=request.store_phone
        )
        db.add(config)
    else:
        config.is_open = bool(request.is_open)
        config.open_time = open_t
        config.close_time = close_t
        config.store_name = request.store_name
        config.delivery_fee = request.delivery_fee
        config.min_order_amount = request.min_order_amount
        config.store_address = request.store_address
        config.store_phone = request.store_phone
        
    await db.commit()
    
    return success(msg="设置已更新")

# --- Category Management ---

@router.get("/category/list", response_model=ResponseModel[List[product_schemas.CategoryOut]])
async def list_categories(
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """分类列表"""
    result = await db.execute(select(Category).order_by(Category.sort_order.desc()))
    categories = result.scalars().all()
    return success(data=categories)

@router.post("/category/create", response_model=ResponseModel)
async def create_category(
    request: product_schemas.CategoryCreate,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """创建分类"""
    category = Category(**request.model_dump())
    db.add(category)
    await db.commit()
    return success(msg="分类创建成功")

@router.post("/category/update", response_model=ResponseModel)
async def update_category(
    id: int,
    request: product_schemas.CategoryUpdate,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """更新分类"""
    category = await db.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
        
    await db.commit()
    return success(msg="分类更新成功")

@router.post("/category/delete", response_model=ResponseModel)
async def delete_category(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """删除分类"""
    category = await db.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    # Check if has products
    result = await db.execute(select(Product).where(Product.category_id == id).limit(1))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该分类下有商品，禁止删除")
        
    await db.delete(category)
    await db.commit()
    return success(msg="分类已删除")

# --- Product Management ---

@router.get("/product/list", response_model=ResponseModel[product_schemas.ProductListOut])
async def list_products(
    page: int = 1,
    size: int = 10,
    name: str = None,
    category_id: int = None,
    status: int = None,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """商品列表 (Admin)"""
    query = select(Product).order_by(Product.created_at.desc())
    
    if name:
        query = query.where(Product.name.ilike(f"%{name}%"))
    if category_id:
        query = query.where(Product.category_id == category_id)
    if status is not None:
        query = query.where(Product.status == status)
        
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()
    
    # Paginate
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    products = result.scalars().all()
    
    return success(data={
        "list": products,
        "total": total,
        "page": page,
        "size": size
    })

@router.post("/product/save", response_model=ResponseModel)
async def save_product(
    request: product_schemas.ProductUpdate,
    id: int = None, # If provided, update; else create
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """保存商品 (新增/编辑)"""
    if id:
        # Update
        product = await db.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        msg = "商品更新成功"
    else:
        # Create
        # Validate required fields for create (since ProductUpdate has optionals)
        # In a real scenario, we might want a separate Create schema or manual check
        if not request.name or not request.price or not request.category_id:
             raise HTTPException(status_code=400, detail="Missing required fields")
             
        product = Product(**request.model_dump())
        db.add(product)
        msg = "商品创建成功"
        
    await db.commit()
    return success(msg=msg)

@router.post("/product/delete", response_model=ResponseModel)
async def delete_product(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """删除商品"""
    product = await db.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    await db.delete(product)
    await db.commit()
    return success(msg="商品已删除")

@router.post("/product/status", response_model=ResponseModel)
async def update_product_status(
    id: int,
    status: int, # 0 or 1
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """上下架商品"""
    product = await db.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    product.status = status
    await db.commit()
    return success(msg="状态已更新")

# --- User Management ---

@router.get("/user/list", response_model=ResponseModel[user_schemas.UserListOut])
async def list_users(
    page: int = 1,
    size: int = 10,
    phone: str = None,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """用户列表"""
    query = select(User).order_by(User.created_at.desc())
    
    if phone:
        query = query.where(User.phone.ilike(f"%{phone}%"))
        
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()
    
    # Paginate
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return success(data={
        "list": users,
        "total": total,
        "page": page,
        "size": size
    })
