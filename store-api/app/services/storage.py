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

    @abstractmethod
    def get_file_url(self, path: str) -> str:
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
        
        # Return relative path (object_name) for flexible storage
        # The full URL can be generated using get_file_url(object_name)
        return object_name

    def get_file_url(self, path: str) -> str:
        """
        获取文件的完整访问链接 (签名 URL)
        """
        # Return Signed URL (valid for 1 year = 31536000 seconds)
        # This is required if the bucket is private (ACL=private)
        
        # Ensure endpoint starts with https for the signed URL
        if not self.bucket.endpoint.startswith("http"):
             pass

        url = self.bucket.sign_url('GET', path, 31536000)
        
        # Force HTTPS if the generated URL is HTTP and endpoint didn't specify
        if url.startswith("http://") and "aliyuncs.com" in url:
            url = url.replace("http://", "https://", 1)
            
        return url

class LocalStorage(BaseStorage):
    # Fallback or dev usage
    async def upload(self, file: UploadFile, folder: str = "uploads") -> str:
        # Implementation skipped for now as user requested OSS
        pass

    def get_file_url(self, path: str) -> str:
        return path

def get_storage() -> BaseStorage:
    if settings.UPLOAD_STORAGE_TYPE == "aliyun":
        return AliyunOSSStorage()
    return LocalStorage()

storage = get_storage()
