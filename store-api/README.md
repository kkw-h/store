# Store API

社区购项目后端 API，基于 FastAPI 和 PostgreSQL。

## 目录结构

```
store-api/
├── app/
│   ├── api/v1/       # 接口路由
│   ├── core/         # 核心配置
│   ├── models/       # 数据模型
│   └── services/     # 业务逻辑
├── alembic/          # 数据库迁移
└── main.py           # 入口文件
```

## 快速开始

### 1. 环境准备

确保已安装 Python 3.10+ 和 PostgreSQL。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境

复制环境变量示例文件：

```bash
cp .env.example .env
```

修改 `.env` 中的数据库配置。

### 4. 运行服务

```bash
uvicorn main:app --reload
```

访问文档：`http://localhost:8000/docs`
