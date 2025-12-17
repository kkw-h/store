from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Any
from datetime import datetime

from app.api import deps
from app.models.order import Order, OrderTimeline
from app.models.shop import ShopConfig
from app.schemas import admin as admin_schemas
from app.schemas.response import ResponseModel, success

router = APIRouter()

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
            store_name="社区优选", # 默认名
            is_open=bool(request.is_open),
            open_time=open_t,
            close_time=close_t
        )
        db.add(config)
    else:
        config.is_open = bool(request.is_open)
        config.open_time = open_t
        config.close_time = close_t
        
    await db.commit()
    
    return success(msg="设置已更新")
