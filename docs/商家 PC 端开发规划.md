# 商家 PC 端开发规划文档

## 1. 项目概述
本项目为“社区购”商家端后台管理系统，旨在为商家提供高效的商品管理、订单处理（配送/核销）及店铺基础设置功能。

### 1.1 技术架构
- **核心框架**: Vue 3 + Vite
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **路由管理**: Vue Router 4
- **HTTP 客户端**: Axios
- **CSS 预处理**: Sass

## 2. 目录结构规范
```text
src/
├── api/             # API 接口管理 (按模块划分)
│   ├── auth.js      # 认证相关
│   ├── product.js   # 商品管理
│   ├── order.js     # 订单管理
│   └── shop.js      # 店铺设置
├── assets/          # 静态资源 (images, styles)
├── components/      # 公共组件
├── layout/          # 布局组件
│   ├── index.vue    # 主布局入口
│   ├── Sidebar/     # 侧边栏
│   └── Header/      # 顶部导航
├── router/          # 路由配置
│   └── index.js     # 路由定义与守卫
├── stores/          # Pinia 状态管理
│   └── user.js      # 用户状态 (Token, UserInfo)
├── utils/           # 工具函数
│   ├── request.js   # Axios 封装
│   └── auth.js      # Token 存储
├── views/           # 页面视图
│   ├── login/       # 登录页
│   ├── dashboard/   # 工作台
│   ├── product/     # 商品管理 (列表, 编辑)
│   ├── order/       # 订单管理 (列表, 详情)
│   └── shop/        # 店铺设置
└── App.vue
```

## 3. 接口映射表
基于后端代码分析，关键接口路径如下：

| 模块 | 功能 | 接口路径 | 方法 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| **认证** | 管理员登录 | `/api/v1/auth/admin/login` | POST | 修正原文档路径 |
| **商品** | 商品列表 | `/api/v1/admin/product/list` | GET | |
| **商品** | 商品保存 | `/api/v1/admin/product/save` | POST | 新增/编辑 |
| **商品** | 上下架 | `/api/v1/admin/product/status` | POST | |
| **订单** | 订单列表 | `/api/v1/admin/order/list` | GET | |
| **订单** | 订单详情 | `/api/v1/admin/order/detail` | GET | |
| **订单** | 接单/拒单 | `/api/v1/admin/order/audit` | POST | 配送单 |
| **订单** | 确认送达 | `/api/v1/admin/order/complete_delivery` | POST | 配送单 |
| **订单** | 扫码核销 | `/api/v1/admin/order/verify` | POST | 自提单 |
| **配置** | 获取配置 | `/api/v1/admin/shop/config` | GET | |
| **配置** | 更新配置 | `/api/v1/admin/shop/config` | POST | |

## 4. 开发阶段规划

### Phase 1: 基础架构 (Completed)
- [x] 项目初始化 (Vite + Vue3 + Element Plus)
- [x] 基础工具类封装 (Axios, Auth)
- [x] 登录页面开发
- [x] 主布局 (Layout) 搭建
- [x] 路由与权限控制

### Phase 2: 商品管理 (Completed)
- [x] 分类管理 (CRUD)
- [x] 商品列表 (筛选, 分页)
- [x] 商品编辑 (图片上传, 规格设置)

### Phase 3: 订单管理 (Completed)
- [x] 订单列表 (多状态 Tab)
- [x] 订单详情页
- [ ] 修改订单商品数量
- [x] 配送流程 (接单 -> 送达)
- [x] 自提流程 (核销码验证)

### Phase 4: 店铺设置与 Dashboard
- [ ] 店铺基础设置 (营业时间, 运费)
- [ ] 数据看板 (今日数据, 待处理事项)

### Phase 5: 完善功能 (Completed)
- [x] 用户管理 (列表)
