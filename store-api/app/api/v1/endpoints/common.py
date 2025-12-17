from typing import Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.response import ResponseModel, success
from app.schemas.file import FileOut
from app.services.storage import storage

router = APIRouter()

@router.post("/upload", response_model=ResponseModel[FileOut])
async def upload_file(
    file: UploadFile = File(...),
) -> Any:
    """
    通用文件上传接口
    
    - 支持图片、视频等文件
    - 返回文件存储路径 (Relative Path) 和 访问链接 (URL)
    - 目前使用阿里云 OSS
    """
    try:
        path = await storage.upload(file)
        url = storage.get_file_url(path)
        return success(data={"path": path, "url": url})
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
