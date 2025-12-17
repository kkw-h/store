from typing import Any
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas import cart as cart_schemas
from app.schemas.response import ResponseModel, success

router = APIRouter()

@router.post("/add", response_model=ResponseModel[cart_schemas.CartItemOut])
async def add_to_cart(
    cart_in: cart_schemas.CartAdd,
    session: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    添加商品到购物车
    """
    # Check product
    product = await session.get(Product, cart_in.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.status != 1:
        raise HTTPException(status_code=400, detail="Product is off shelves")
    
    # Check if item exists
    result = await session.execute(
        select(CartItem).where(
            CartItem.user_id == current_user.id,
            CartItem.product_id == cart_in.product_id
        )
    )
    cart_item = result.scalars().first()
    
    if cart_item:
        cart_item.quantity += cart_in.quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=cart_in.product_id,
            quantity=cart_in.quantity,
            selected=True
        )
        session.add(cart_item)
    
    await session.commit()
    await session.refresh(cart_item)
    
    # Construct response
    return success(data={
        "id": cart_item.id,
        "product_id": product.id,
        "product_name": product.name,
        "product_image": product.thumb_url,
        "price": product.price,
        "quantity": cart_item.quantity,
        "selected": cart_item.selected,
        "stock": product.stock
    })

@router.get("/list", response_model=ResponseModel[cart_schemas.CartListOut])
async def list_cart(
    session: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    获取购物车列表
    """
    result = await session.execute(
        select(CartItem)
        .where(CartItem.user_id == current_user.id)
        .options(selectinload(CartItem.product))
        .order_by(CartItem.created_at.desc())
    )
    items = result.scalars().all()
    
    cart_list = []
    total_amount = Decimal(0)
    selected_count = 0
    
    for item in items:
        if not item.product:
            # Should not happen ideally, but if product deleted
            continue
            
        cart_item_out = {
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "product_image": item.product.thumb_url,
            "price": item.product.price,
            "quantity": item.quantity,
            "selected": item.selected,
            "stock": item.product.stock
        }
        cart_list.append(cart_item_out)
        
        if item.selected:
            total_amount += item.product.price * item.quantity
            selected_count += item.quantity
            
    return success(data={
        "list": cart_list,
        "total_amount": total_amount,
        "selected_count": selected_count
    })

@router.put("/update", response_model=ResponseModel)
async def update_cart(
    update_in: cart_schemas.CartUpdate,
    session: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    更新购物车项 (数量/选中状态)
    """
    result = await session.execute(
        select(CartItem).where(
            CartItem.id == update_in.id,
            CartItem.user_id == current_user.id
        )
    )
    cart_item = result.scalars().first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if update_in.quantity is not None:
        cart_item.quantity = update_in.quantity
        
    if update_in.selected is not None:
        cart_item.selected = update_in.selected
        
    await session.commit()
    return success(msg="Updated successfully")

@router.delete("/delete", response_model=ResponseModel)
async def delete_cart(
    delete_in: cart_schemas.CartDelete,
    session: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    删除购物车项
    """
    await session.execute(
        delete(CartItem).where(
            CartItem.id.in_(delete_in.ids),
            CartItem.user_id == current_user.id
        )
    )
    await session.commit()
    return success(msg="Deleted successfully")
