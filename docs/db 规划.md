# 🐘 PostgreSQL 数据库设计文档 (V1.0)

## 1. 设计规范
*   **字符集：** UTF8
*   **金额类型：** 使用 `NUMERIC(10, 2)`，**严禁**使用 Float/Double（避免精度丢失）。
*   **时间类型：** 使用 `TIMESTAMPTZ` (带时区的时间戳)，确保跨时区或服务器迁移时时间准确。
*   **主键：** 使用 `BIGSERIAL` (自增长整型)。
*   **快照机制：** 订单中的地址和商品信息采用 **JSONB** 存储快照，防止用户修改地址或商家修改商品后，历史订单数据错乱。

---

## 2. SQL 建表脚本

你可以直接将以下 SQL 复制到你的 PostgreSQL 客户端（如 PgAdmin, DBeaver）中执行。

### 2.1 基础配置与用户

```sql
-- 1. 店铺配置表 (单店模式，通常只有一条记录)
CREATE TABLE shop_config (
    id SERIAL PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    store_address VARCHAR(255),
    store_phone VARCHAR(20),
    is_open BOOLEAN DEFAULT TRUE COMMENT '总开关: true营业 false打烊',
    open_time TIME NOT NULL DEFAULT '09:00:00',
    close_time TIME NOT NULL DEFAULT '22:00:00',
    delivery_fee NUMERIC(10, 2) DEFAULT 0.00 COMMENT '基础运费',
    min_order_amount NUMERIC(10, 2) DEFAULT 0.00 COMMENT '起送金额',
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE shop_config IS '店铺全局配置表';

-- 2. 用户表 (C端用户)
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    openid VARCHAR(64) NOT NULL UNIQUE COMMENT '微信OpenID',
    nickname VARCHAR(64),
    avatar_url VARCHAR(255),
    phone VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_openid ON users(openid);
COMMENT ON TABLE users IS '用户信息表';

-- 3. 用户地址表
CREATE TABLE user_addresses (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    contact_name VARCHAR(64) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    detail_address VARCHAR(255) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_addr_user_id ON user_addresses(user_id);
```

### 2.2 商品管理

```sql
-- 4. 商品分类表
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    sort_order INT DEFAULT 0 COMMENT '排序权重，越大越前',
    is_visible BOOLEAN DEFAULT TRUE
);

-- 5. 商品表
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    category_id INT REFERENCES categories(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    thumb_url VARCHAR(255) COMMENT '商品缩略图',
    price NUMERIC(10, 2) NOT NULL COMMENT '当前售价',
    original_price NUMERIC(10, 2) COMMENT '原价/划线价',
    stock INT DEFAULT 0 NOT NULL COMMENT '库存',
    sales_count INT DEFAULT 0 COMMENT '销量(展示用)',
    status INT DEFAULT 1 COMMENT '1:上架 0:下架',
    specs JSONB DEFAULT NULL COMMENT '预留字段：多规格信息',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_cat_status ON products(category_id, status);
```

### 2.3 订单核心 (最关键部分)

```sql
-- 6. 订单主表
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    order_no VARCHAR(32) NOT NULL UNIQUE COMMENT '业务订单号，如 20231217xxxx',
    user_id BIGINT NOT NULL REFERENCES users(id),
    
    -- 金额信息
    total_amount NUMERIC(10, 2) NOT NULL COMMENT '商品总价',
    delivery_fee NUMERIC(10, 2) DEFAULT 0.00 COMMENT '运费',
    final_amount NUMERIC(10, 2) NOT NULL COMMENT '实付金额',
    
    -- 订单状态与类型
    -- 状态码: 0:待支付, 1:待接单(配送), 2:待自提, 3:配送中, 4:已完成, -1:已取消/退款
    status INT NOT NULL DEFAULT 0,
    delivery_type VARCHAR(20) NOT NULL COMMENT '枚举: delivery / pickup',
    
    -- 配送信息 (JSONB快照)
    -- 结构: { "name": "张三", "phone": "138...", "address": "xx路xx号" }
    address_snapshot JSONB, 
    
    -- 自提信息
    pickup_code VARCHAR(10) COMMENT '6位核销码',
    pickup_time TIMESTAMPTZ COMMENT '预约自提时间',
    verified_at TIMESTAMPTZ COMMENT '核销/完成时间',
    
    -- 支付与备注
    transaction_id VARCHAR(64) COMMENT '微信支付流水号',
    remark VARCHAR(255) COMMENT '用户备注',
    reject_reason VARCHAR(255) COMMENT '商家拒单原因',
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user_status ON orders(user_id, status);
CREATE INDEX idx_orders_pickup_code ON orders(pickup_code); -- 加速核销查询

-- 7. 订单明细表 (记录买了什么)
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    product_id BIGINT REFERENCES products(id),
    
    -- 快照信息 (防止商品改名或改价后历史订单显示错误)
    product_name VARCHAR(100) NOT NULL,
    product_image VARCHAR(255),
    price NUMERIC(10, 2) NOT NULL COMMENT '购买时的单价',
    quantity INT NOT NULL DEFAULT 1
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
```

---

## 3. 核心字段逻辑说明

### 3.1 为什么使用 JSONB (`address_snapshot`)？
在 `orders` 表中，我没有直接关联 `user_addresses.id`，而是存了一个 `JSONB`。
*   **原因：** 如果用户下单后修改了地址簿里的电话号码，历史订单不应该随之改变。订单必须记录“下单那一刻”的地址信息。
*   **数据样例：**
    ```json
    {
      "name": "Monica",
      "phone": "13800138000",
      "detail": "幸福小区5号楼101",
      "province": "广东省",
      "city": "深圳市"
    }
    ```

### 3.2 状态码映射 (Status Mapping)
后端代码中建议定义常量或枚举来对应数据库的 `status` 字段：

| 数据库值 (`int`) | 含义 | 适用场景 |
| :--- | :--- | :--- |
| `0` | PENDING_PAY | 待支付 |
| `1` | PENDING_ACCEPT | 待接单 (仅配送模式) |
| `2` | PENDING_PICKUP | 待自提 (仅自提模式，生成了核销码) |
| `3` | DELIVERING | 配送中 (商家已接单) |
| `4` | COMPLETED | 已完成 (已送达 或 已核销) |
| `-1` | CANCELLED | 已取消 / 拒单退款 |

### 3.3 核销码 (`pickup_code`)
*   该字段加了**唯一索引** (虽然业务逻辑上不同订单可能撞码，但建议结合 `status` 查询)。
*   为了查询效率，我特意加了 `CREATE INDEX idx_orders_pickup_code`。当商家输入6位码时，数据库能毫秒级定位到订单。

---

## 4. 常用 SQL 查询示例

### 4.1 商家端：查询“待处理”的订单
```sql
-- 查询所有 待接单(1) 和 待自提(2) 的订单，按时间倒序
SELECT * FROM orders 
WHERE status IN (1, 2) 
ORDER BY created_at ASC;
```

### 4.2 商家端：核销逻辑
```sql
-- 1. 查找订单 (假设商家输入了 884512)
SELECT * FROM orders 
WHERE pickup_code = '884512' AND status = 2;

-- 2. 如果找到，更新状态为已完成
UPDATE orders 
SET status = 4, verified_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
WHERE id = {查到的订单ID};
```

### 4.3 用户端：查询我的订单
```sql
SELECT o.id, o.order_no, o.status, o.final_amount, 
       i.product_name, i.product_image -- 简单展示第一个商品
FROM orders o
JOIN order_items i ON o.id = i.order_id
WHERE o.user_id = {当前用户ID}
ORDER BY o.created_at DESC;
```