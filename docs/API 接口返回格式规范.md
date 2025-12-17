## 1. 📦 JSON 响应结构概览

无论请求成功还是失败，接口始终返回 HTTP 状态码 **200 OK**（除了极端的网关层错误），具体的业务结果通过 JSON Body 中的 `code` 字段判断。

### 通用结构
```json
{
  "code": 200,          // 业务状态码：200表示成功，其他为失败
  "msg": "操作成功",     // 提示信息：用于前端直接弹窗展示
  "data": { ... }       // 业务数据：对象、数组或 null
}
```

---

## 2. 📝 详细场景示例

### 2.1 成功 - 返回单条数据 (Object)
*场景：获取订单详情、获取用户信息*
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 101,
    "name": "红富士苹果",
    "price": "5.50"
  }
}
```

### 2.2 成功 - 返回列表数据 (Pagination)
*场景：商品列表、订单列表*
*规范：列表数据必须包含 `list` (数组) 和 `total` (总数)，方便前端做分页组件。*
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "list": [
      { "id": 1, "name": "A" },
      { "id": 2, "name": "B" }
    ],
    "total": 52,        // 总记录数
    "page": 1,          // 当前页码
    "size": 10          // 每页数量
  }
}
```

### 2.3 成功 - 无数据返回
*场景：删除操作、修改密码、发送验证码*
```json
{
  "code": 200,
  "msg": "删除成功",
  "data": null
}
```

### 2.4 失败 - 业务逻辑错误
*场景：库存不足、密码错误、未登录*
*前端逻辑：检测到 `code !== 200`，直接拦截并 `Toast(msg)`。*
```json
{
  "code": 4001,           // 具体的错误码
  "msg": "库存不足，当前仅剩2件", // 给用户看的提示
  "data": null
}
```

---

## 3. 🔢 状态码定义 (Status Codes)

建议维护一份全局的状态码枚举，不要随意定义数字。

| 状态码 (`code`) | 说明 | 前端动作 |
| :--- | :--- | :--- |
| **200** | **成功 (Success)** | 正常解析 `data` |
| **400** | **参数错误** | 弹出提示“参数有误” |
| **401** | **未授权 (Unauthorized)** | **强制跳转到登录页** |
| **403** | **无权限 (Forbidden)** | 提示“您无权进行此操作” |
| **500** | **服务器内部错误** | 提示“系统繁忙，请稍后再试” |
| **1001** | 业务通用错误 | 直接弹出 `msg` 内容 |
| **2001** | 库存不足 | 提示并刷新页面 |
| **2002** | 订单状态已改变 | 提示并刷新页面 |

---

## 4. 🐍 Python (FastAPI) 实现方案

在 FastAPI 中，我们可以使用 **Pydantic 的泛型 (Generics)** 来定义这个标准结构，这样 Swagger 文档也能自动生成正确的格式。

请在 `app/schemas/response.py` 中创建以下代码：

```python
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

# 定义泛型变量 T
T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    code: int = 200
    msg: str = "success"
    data: Optional[T] = None

    class Config:
        # 允许通过别名映射 (如果需要兼容旧系统)
        populate_by_name = True

# 辅助函数：快速构造成功响应
def success(data: T = None, msg: str = "success"):
    return {"code": 200, "msg": msg, "data": data}

# 辅助函数：快速构造失败响应
def error(code: int = 500, msg: str = "error", data: T = None):
    return {"code": code, "msg": msg, "data": data}
```

### 在 API 接口中使用

```python
from fastapi import APIRouter
from app.schemas.response import ResponseModel
from app.schemas.user import UserDTO # 假设你有一个用户数据模型

router = APIRouter()

# 重点：response_model 使用泛型包装
@router.get("/user/info", response_model=ResponseModel[UserDTO])
async def get_user_info():
    user_data = {"id": 1, "name": "Monica"}
    
    # 直接返回字典，FastAPI 会自动验证并包装成 ResponseModel
    return {
        "code": 200,
        "msg": "获取成功",
        "data": user_data
    }
```

### 统一异常处理 (Global Exception Handler)

为了防止程序报错（如 `500 Internal Server Error`）直接返回 HTML 页面给前端，你需要拦截所有异常并格式化为 JSON。

在 `app/main.py` 中添加：

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

# 1. 捕获参数校验错误 (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=200, # 即使是校验错误，HTTP层也返200，方便前端拦截
        content={
            "code": 400,
            "msg": f"参数错误: {exc.errors()[0]['msg']}",
            "data": None
        }
    )

# 2. 捕获通用异常 (500)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "code": 500,
            "msg": "服务器开小差了，请稍后再试",
            "data": str(exc) # 生产环境建议隐藏具体错误信息
        }
    )
```