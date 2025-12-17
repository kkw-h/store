from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.api import deps
from app.models.user import User, UserAddress
from app.schemas import address as address_schemas
from app.schemas.response import ResponseModel, success

router = APIRouter()

@router.post("", response_model=ResponseModel[address_schemas.AddressOut])
async def create_address(
    address_in: address_schemas.AddressCreate,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    创建收货地址
    
    - 支持设置默认地址
    - 如果设置为默认，会自动取消该用户其他地址的默认状态
    """
    # 如果新增地址设为默认，则先将该用户所有其他地址设为非默认
    if address_in.is_default:
        await session.execute(
            update(UserAddress)
            .where(UserAddress.user_id == current_user.id)
            .values(is_default=False)
        )

    # 创建新地址记录
    new_address = UserAddress(
        user_id=current_user.id,
        **address_in.model_dump()
    )
    session.add(new_address)
    await session.commit()
    await session.refresh(new_address)
    
    return success(data=new_address)

@router.get("", response_model=ResponseModel[List[address_schemas.AddressOut]])
async def read_addresses(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    获取收货地址列表
    
    - 排序规则: 默认地址优先，其次按创建时间倒序
    """
    result = await session.execute(
        select(UserAddress)
        .where(UserAddress.user_id == current_user.id)
        .order_by(UserAddress.is_default.desc(), UserAddress.created_at.desc())
    )
    addresses = result.scalars().all()
    return success(data=addresses)

@router.put("/{address_id}", response_model=ResponseModel[address_schemas.AddressOut])
async def update_address(
    address_id: int,
    address_in: address_schemas.AddressUpdate,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    更新收货地址
    
    - 支持部分更新
    - 如果更新为默认地址，会自动互斥处理
    """
    # 查询待更新的地址，确保属于当前用户
    result = await session.execute(
        select(UserAddress)
        .where(UserAddress.id == address_id, UserAddress.user_id == current_user.id)
    )
    address = result.scalars().first()
    
    if not address:
        raise HTTPException(status_code=404, detail="地址未找到")

    # 如果要设置为默认地址，则取消其他地址的默认状态
    if address_in.is_default:
        await session.execute(
            update(UserAddress)
            .where(UserAddress.user_id == current_user.id)
            .where(UserAddress.id != address_id)
            .values(is_default=False)
        )
    
    # 更新字段
    update_data = address_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(address, field, value)
    
    session.add(address)
    await session.commit()
    await session.refresh(address)
    
    return success(data=address)

@router.delete("/{address_id}", response_model=ResponseModel[None])
async def delete_address(
    address_id: int,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    删除收货地址
    
    - 物理删除
    """
    result = await session.execute(
        select(UserAddress)
        .where(UserAddress.id == address_id, UserAddress.user_id == current_user.id)
    )
    address = result.scalars().first()
    
    if not address:
        raise HTTPException(status_code=404, detail="地址未找到")
        
    await session.delete(address)
    await session.commit()
    
    return success(msg="地址删除成功")
