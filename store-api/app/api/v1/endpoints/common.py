from typing import Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.response import ResponseModel, success
from app.services.storage import storage

router = APIRouter()

@router.post("/upload", response_model=ResponseModel[str])
async def upload_file(
    file: UploadFile = File(...),
) -> Any:
    """
    通用文件上传接口
    
    - 支持图片、视频等文件
    - 返回文件访问 URL
    - 目前使用阿里云 OSS
    """
    try:
        url = await storage.upload(file)
        return success(data=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/payment/notify")
async def payment_notify(request: dict) -> Any:
    """
    微信支付回调接口 (Mock)
    """
    # TODO: Validate signature, parse XML/JSON from WeChat
    # For now just log it
    print(f"Received payment notify: {request}")
    return {"code": "SUCCESS", "message": "OK"}
