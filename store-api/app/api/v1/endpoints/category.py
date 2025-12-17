from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.product import Category, Product
from app.schemas import product as product_schemas
from app.schemas.response import ResponseModel, success

router = APIRouter()

@router.post("", response_model=ResponseModel[product_schemas.CategoryOut])
async def create_category(
    category_in: product_schemas.CategoryCreate,
    session: AsyncSession = Depends(deps.get_db),
    # current_user: User = Depends(deps.get_current_active_superuser), # TODO: Add admin permission check
) -> Any:
    """
    创建商品分类
    """
    category = Category(**category_in.model_dump())
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return success(data=category)

@router.get("/list", response_model=ResponseModel[List[product_schemas.CategoryOut]])
async def read_categories(
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    获取分类列表 (左侧导航)
    
    - 仅返回可见 (is_visible=True) 的分类
    - 按 sort_order 倒序排列
    """
    result = await session.execute(
        select(Category)
        .where(Category.is_visible == True)
        .order_by(Category.sort_order.desc(), Category.id.asc())
    )
    categories = result.scalars().all()
    return success(data=categories)

@router.get("/{category_id}", response_model=ResponseModel[product_schemas.CategoryOut])
async def read_category(
    category_id: int,
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    获取分类详情
    """
    result = await session.execute(select(Category).where(Category.id == category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return success(data=category)

@router.put("/{category_id}", response_model=ResponseModel[product_schemas.CategoryOut])
async def update_category(
    category_id: int,
    category_in: product_schemas.CategoryUpdate,
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    更新分类信息
    """
    result = await session.execute(select(Category).where(Category.id == category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return success(data=category)

@router.delete("/{category_id}", response_model=ResponseModel[None])
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    删除分类
    
    - 如果分类下有商品，禁止删除
    """
    result = await session.execute(select(Category).where(Category.id == category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if products exist in this category
    products_result = await session.execute(select(Product).where(Product.category_id == category_id))
    if products_result.scalars().first():
        raise HTTPException(status_code=400, detail="Cannot delete category with existing products")

    await session.delete(category)
    await session.commit()
    return success(msg="Category deleted successfully")
