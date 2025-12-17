from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl

class Settings(BaseSettings):
    """
    项目全局配置类 (Global Configuration)
    
    通过 Pydantic Settings 管理环境变量。
    自动从 .env 文件读取配置信息。
    """
    # 项目基础信息
    PROJECT_NAME: str = "Store API"
    API_V1_STR: str = "/api/v1"
    
    # 安全配置 (Security)
    SECRET_KEY: str  # JWT 签名密钥
    ALGORITHM: str   # 加密算法 (如 HS256)
    ACCESS_TOKEN_EXPIRE_MINUTES: int  # Token 过期时间(分钟)
    
    # 微信小程序配置 (WeChat Mini Program)
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""

    # 数据库配置 (Database)
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """
        构建 SQLAlchemy 异步数据库连接 URL
        格式: postgresql+asyncpg://user:password@host:port/dbname
        """
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
