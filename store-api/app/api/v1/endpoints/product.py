from typing import List, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api import deps
from app.models.product import Product, Category
from app.schemas import product as product_schemas
from app.schemas.response import ResponseModel, success

router = APIRouter()

@router.post("", response_model=ResponseModel[product_schemas.ProductOut])
async def create_product(
    product_in: product_schemas.ProductCreate,
    session: AsyncSession = Depends(deps.get_db),
    # current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    创建商品
    """
    # Check if category exists
    category = await session.get(Category, product_in.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    product = Product(**product_in.model_dump())
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return success(data=product)

@router.get("/list", response_model=ResponseModel[product_schemas.ProductListOut])
async def read_products(
    category_id: Optional[int] = Query(None, description="分类ID"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    获取商品列表 (分页)
    
    - 支持按 category_id 筛选
    - 支持按 keyword 模糊搜索 (匹配 name)
    - 仅返回上架商品 (status=1)
    """
    # 构建查询
    query = select(Product).where(Product.status == 1)
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    if keyword:
        query = query.where(Product.name.ilike(f"%{keyword}%"))
    
    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()
    
    # 分页查询
    # Note: Product model doesn't have sort_order in my previous definition, so using id desc
    query = query.order_by(Product.id.desc())
    query = query.offset((page - 1) * size).limit(size)
    
    result = await session.execute(query)
    products = result.scalars().all()
    
    return success(data={
        "list": products,
        "total": total,
        "page": page,
        "size": size
    })

@router.get("/{product_id}", response_model=ResponseModel[product_schemas.ProductOut])
async def read_product(
    product_id: int,
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    获取商品详情
    """
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return success(data=product)

@router.put("/{product_id}", response_model=ResponseModel[product_schemas.ProductOut])
async def update_product(
    product_id: int,
    product_in: product_schemas.ProductUpdate,
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    更新商品
    """
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product_in.category_id is not None:
        category = await session.get(Category, product_in.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return success(data=product)

@router.delete("/{product_id}", response_model=ResponseModel[None])
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    删除商品
    """
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    await session.delete(product)
    await session.commit()
    return success(msg="Product deleted successfully")
