from fastapi import APIRouter
from app.api.v1.endpoints import auth, address, category, product, order, admin, common

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(common.router, tags=["common"]) # No prefix for /upload typically, or /common? Doc says /upload directly? 
# Docs says /upload. But usually we put it under v1. So /api/v1/upload.
# If I use prefix="/common", it becomes /api/v1/common/upload.
# I will use no prefix for common router, so it matches /upload defined in router.
api_router.include_router(address.router, prefix="/address", tags=["address"])
api_router.include_router(category.router, prefix="/category", tags=["category"])
api_router.include_router(product.router, prefix="/product", tags=["product"])
api_router.include_router(order.router, prefix="/order", tags=["order"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
