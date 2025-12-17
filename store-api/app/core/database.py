from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# 创建异步数据库引擎
# echo=True 可以打印 SQL 语句，生产环境建议关闭
engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))

# 创建异步 Session 工厂
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """
    SQLAlchemy 声明式基类
    所有模型都应继承此类
    """
    pass

async def get_db():
    """
    依赖注入: 获取数据库会话 (AsyncSession)
    
    Yields:
        AsyncSession: 数据库会话对象
    """
    async with SessionLocal() as session:
        yield session
