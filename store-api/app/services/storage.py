from abc import ABC, abstractmethod
import os
import uuid
import oss2
import time
from datetime import datetime
from fastapi import UploadFile
from app.core.config import settings

class BaseStorage(ABC):
    @abstractmethod
    async def upload(self, file: UploadFile, folder: str = "uploads") -> str:
        pass

class AliyunOSSStorage(BaseStorage):
    def __init__(self):
        self.auth = oss2.Auth(
            settings.ALIYUN_OSS_ACCESS_KEY_ID, 
            settings.ALIYUN_OSS_ACCESS_KEY_SECRET
        )
        self.bucket = oss2.Bucket(
            self.auth, 
            settings.ALIYUN_OSS_ENDPOINT, 
            settings.ALIYUN_OSS_BUCKET_NAME
        )
        # Use simple upload for now, maybe multipart for large files later
        
    async def upload(self, file: UploadFile, folder: str = "uploads") -> str:
        # Determine file type folder
        content_type = file.content_type
        if content_type.startswith("image/"):
            type_folder = "images"
        elif content_type.startswith("video/"):
            type_folder = "videos"
        elif content_type.startswith("audio/"):
            type_folder = "audios"
        else:
            type_folder = "files"
            
        # Generate filename with timestamp
        # Format: {folder}/{type_folder}/{YYYYMMDD}/{HHMMSS}_{uuid}{ext}
        ext = os.path.splitext(file.filename)[1]
        now = datetime.now()
        date_folder = now.strftime("%Y%m%d")
        time_prefix = now.strftime("%H%M%S")
        unique_id = uuid.uuid4().hex[:8] # Shorten uuid to 8 chars
        
        # Example: uploads/images/20231220/143000_a1b2c3d4.png
        object_name = f"{folder}/{type_folder}/{date_folder}/{time_prefix}_{unique_id}{ext}"
        
        # Read file content
        content = await file.read()
        
        # Upload
        # put_object is synchronous in oss2, so it might block the event loop slightly. 
        # Ideally run in threadpool for large files, but for small images it's ok.
        self.bucket.put_object(object_name, content)
        
        # Return URL
        # Assuming public read bucket. If private, need to sign url.
        # Format: https://{bucket}.{endpoint}/{object}
        # Note: endpoint usually contains protocol or not? 
        # config says "oss-cn-beijing.aliyuncs.com"
        url = f"https://{settings.ALIYUN_OSS_BUCKET_NAME}.{settings.ALIYUN_OSS_ENDPOINT}/{object_name}"
        return url

class LocalStorage(BaseStorage):
    # Fallback or dev usage
    async def upload(self, file: UploadFile, folder: str = "uploads") -> str:
        # Implementation skipped for now as user requested OSS
        pass

def get_storage() -> BaseStorage:
    if settings.UPLOAD_STORAGE_TYPE == "aliyun":
        return AliyunOSSStorage()
    return LocalStorage()

storage = get_storage()
