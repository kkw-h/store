from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.api.v1.api import api_router
from app.schemas.response import error

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Store API 接口文档"
)

# 1. 捕获参数校验错误 (422)
# 将 FastAPI 默认的 422 错误转换为自定义的 400 格式
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=200,
        content=error(
            code=400,
            msg=f"参数错误: {exc.errors()[0]['msg']}"
        )
    )

# 2. 捕获 HTTP 异常 (代码中主动抛出的 HTTPException)
# 保持 HTTP 状态码为 200，通过 body 中的 code 区分业务错误
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=200,
        content=error(
            code=exc.status_code if exc.status_code != 200 else 400, # 如果抛出 400，code=400。如果抛出 404，code=404。
            msg=str(exc.detail),
            data=None
        )
    )

# 3. 捕获全局通用异常 (500)
# 兜底处理所有未捕获的异常，防止服务器报错信息直接暴露给前端
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content=error(
            code=500,
            msg="服务器开小差了，请稍后再试",
            data=str(exc) if settings.PROJECT_NAME else None # 生产环境建议隐藏具体错误信息
        )
    )

# 注册 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to Store API"}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}
