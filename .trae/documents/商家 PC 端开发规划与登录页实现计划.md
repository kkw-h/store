# 商家 PC 端开发规划与登录页实现计划

## 1. 商家 PC 端开发规划文档

我将创建文档 `docs/商家 PC 端开发规划.md`，明确项目架构与开发路径。

### 1.1 技术架构
- **核心框架**: Vue 3 + Vite
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **路由管理**: Vue Router 4
- **HTTP 客户端**: Axios
- **CSS 预处理**: Sass

### 1.2 目录结构规范
```text
src/
├── api/             # API 接口管理 (按模块划分: auth, product, order...)
├── assets/          # 静态资源
├── components/      # 公共组件
├── layout/          # 布局组件 (Sidebar, Header, AppMain)
├── router/          # 路由配置 & 权限守卫
├── stores/          # Pinia 状态管理
├── utils/           # 工具函数 (request.js, auth.js 等)
├── views/           # 页面视图
│   ├── login/       # 登录页
│   ├── dashboard/   # 工作台
│   ├── product/     # 商品管理
│   ├── order/       # 订单管理
│   └── shop/        # 店铺设置
└── App.vue
```

### 1.3 接口映射修正
基于代码分析，确认以下关键接口路径：
- **管理员登录**: `POST /api/v1/auth/admin/login` (修正原文档的 `/auth/login`)
- **管理端接口前缀**: `/api/v1/admin/...` (如 `/admin/order/list`)

## 2. 登录页面实施计划 (本阶段任务)

### 2.1 基础建设
1.  **工具类封装**:
    - 创建 `src/utils/request.js`: 封装 Axios，统一处理 Request Header (Token) 和 Response (错误提示、401 跳转)。
    - 创建 `src/utils/auth.js`: 封装 Token 的 LocalStorage 读写操作。
2.  **API 定义**:
    - 创建 `src/api/auth.js`: 定义登录接口调用。
3.  **状态管理**:
    - 创建 `src/stores/user.js`: 使用 Pinia 管理 Token 和 UserInfo，实现 `login` 和 `logout` action。

### 2.2 页面开发
1.  **登录页 UI (`src/views/login/index.vue`)**:
    - 使用 Element Plus `el-card`, `el-form`, `el-input`, `el-button` 构建。
    - 实现表单验证 (必填项校验)。
    - 添加美观的背景和布局。
2.  **路由配置 (`src/router/index.js`)**:
    - 添加 `/login` 路由。
    - 添加全局路由守卫 (`beforeEach`)：
        - 已登录去登录页 -> 重定向到首页。
        - 未登录去受保护页 -> 重定向到登录页。
3.  **主布局 (`src/layout/index.vue`)**:
    - 创建基础 Layout 骨架 (Sidebar + RouterView)，作为登录后的跳转目标。

## 3. 下一步建议
完成登录页后，将按照“商品管理 -> 订单管理 -> 店铺设置”的顺序进行开发。
