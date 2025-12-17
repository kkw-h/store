from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, ConfigDict

# 定义泛型变量 T
T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    """
    通用 API 响应模型
    
    Attributes:
        code (int): 业务状态码 (200 表示成功)
        msg (str): 提示信息
        data (T): 业务数据 (泛型)
    """
    code: int = 200
    msg: str = "success"
    data: Optional[T] = None

    # 允许通过字段别名填充数据
    model_config = ConfigDict(populate_by_name=True)

# 辅助函数: 快速构造成功响应
def success(data: T = None, msg: str = "success"):
    """
    构造成功响应
    
    Args:
        data: 返回的数据
        msg: 提示信息
    """
    return {"code": 200, "msg": msg, "data": data}

# 辅助函数: 快速构造错误响应
def error(code: int = 500, msg: str = "error", data: T = None):
    """
    构造错误响应
    
    Args:
        code: 错误码 (非 200)
        msg: 错误提示
        data: 附加数据 (可选)
    """
    return {"code": code, "msg": msg, "data": data}
