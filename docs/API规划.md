# 📡 社区购小程序 API 接口文档

## 🛠 全局规范 (Global Standards)

*   **通信协议：** HTTPS
*   **数据格式：** JSON
*   **基础路径 (Base URL)：** `https://api.yourdomain.com/api/v1`
*   **鉴权方式：** Header 中携带 Token
    *   Key: `Authorization`
    *   Value: `Bearer {token}`
*   **通用响应结构：**
    ```json
    {
      "code": 0,          // 0表示成功，非0表示错误
      "msg": "success",   // 错误提示信息
      "data": { ... }     // 业务数据
    }
    ```

---

## 1. 🔐 用户认证模块 (Auth)

### 1.1 微信登录
*   **描述：** 使用微信 `wx.login` 获取的 code 换取登录态。
*   **Method：** `POST /auth/login`
*   **请求参数：**
    ```json
    {
      "code": "081238..." // 微信临时登录凭证
    }
    ```
*   **响应数据：**
    ```json
    {
      "token": "eyJhbGci...", // 登录令牌 (后续接口必传)
      "userInfo": { "nickname": "...", "avatar": "..." }
    }
    ```

---

## 2. 🛍 商品与展示模块 (Product)

### 2.1 获取分类列表 (左侧导航)
*   **Method：** `GET /category/list`
*   **响应数据：**
    ```json
    [
      { "id": 1, "name": "新鲜水果" },
      { "id": 2, "name": "时令蔬菜" }
    ]
    ```

### 2.2 获取商品列表 (右侧内容)
*   **Method：** `GET /product/list`
*   **Query 参数：**
    *   `category_id`: (可选) 分类ID，不传则查全部
    *   `keyword`: (可选) 搜索关键词
    *   `page`: 页码
*   **响应数据：**
    ```json
    {
      "list": [
        {
          "id": 101,
          "name": "红富士苹果",
          "thumb_url": "http://...",
          "price": "5.50",
          "original_price": "8.00",
          "stock": 100,
          "tags": ["热销", "今日特价"]
        }
      ],
      "total": 50
    }
    ```

---

## 3. 🧾 订单与交易模块 (Order - User Side)

### 3.1 订单预检 (结算页计算)
*   **描述：** 在用户点击“去结算”时调用，用于计算运费、总价，并校验营业时间。
*   **Method：** `POST /order/preview`
*   **请求参数：**
    ```json
    {
      "items": [{ "product_id": 101, "count": 2 }], // 购买商品
      "delivery_type": "delivery" // 'delivery' 或 'pickup'
    }
    ```
*   **响应数据：**
    ```json
    {
      "total_goods_price": "11.00",
      "delivery_fee": "3.00",       // 运费
      "final_price": "14.00",       // 应付总额
      "is_open": true,              // 当前是否在营业时间内
      "delivery_msg": "满30免运费"   // 提示文案
    }
    ```

### 3.2 创建订单 (下单)
*   **Method：** `POST /order/create`
*   **请求参数：**
    ```json
    {
      "items": [{ "product_id": 101, "count": 2 }],
      "delivery_type": "pickup", // 配送方式：pickup(自提) / delivery(配送)
      "remark": "不要葱",
      // --- 如果是自提 ---
      "pickup_time": "2023-12-17 18:00:00",
      "user_phone": "13800138000",
      // --- 如果是配送 ---
      "address_id": 12, // 用户地址ID
    }
    ```
*   **响应数据：**
    ```json
    {
      "order_id": 202312170001,
      "pay_params": { ... } // 微信支付所需参数 (timeStamp, nonceStr, package...)
    }
    ```
    *逻辑说明：后端需在此接口校验库存、校验自提时间是否在营业范围内。*

### 3.3 订单列表
*   **Method：** `GET /order/list`
*   **Query 参数：** `status` (0:全部, 1:待接单, 2:待自提/配送中, 3:已完成)
*   **响应数据：** 包含订单基础信息、商品缩略图、状态文案。

### 3.4 订单详情
*   **Method：** `GET /order/detail`
*   **Query 参数：** `order_id`
*   **响应数据：**
    ```json
    {
      "order_no": "202312170001",
      "status": 2, // 待自提
      "pickup_code": "884512", // 核心：仅自提单且已支付显示此码
      "qrcode_url": "http://...", // 核心：核销二维码图片地址
      "items": [...],
      "timeline": [
        { "status": "下单成功", "time": "10:00" },
        { "status": "商家已接单", "time": "10:05" }
      ]
    }
    ```

---

## 4. 👨‍💼 商家管理模块 (Admin API)

*注意：此模块建议增加管理员权限校验*

### 4.1 商家接单/拒单 (配送单)
*   **描述：** 针对状态为 `1 (待接单)` 的配送订单。
*   **Method：** `POST /admin/order/audit`
*   **请求参数：**
    ```json
    {
      "order_id": 202312170001,
      "action": "accept", // accept(接单) 或 reject(拒单)
      "reject_reason": "距离太远无法配送" // 拒单必填
    }
    ```
*   **逻辑：**
    *   `accept`: 订单状态变更为 `3 (配送中)`，发送微信通知给用户。
    *   `reject`: 触发微信退款接口，订单关闭，发送退款通知。

### 4.2 确认送达 (配送单)
*   **描述：** 商家送完货后点击。
*   **Method：** `POST /admin/order/complete_delivery`
*   **请求参数：** `{ "order_id": ... }`
*   **逻辑：** 订单状态变更为 `4 (已完成)`。

### 4.3 扫码核销 (自提单)
*   **描述：** 商家扫描用户二维码或输入6位数字码。
*   **Method：** `POST /admin/order/verify`
*   **请求参数：**
    ```json
    {
      "code": "884512" // 扫码得到的6位数字
    }
    ```
*   **响应数据：**
    ```json
    {
      "success": true,
      "order_info": { "order_no": "...", "items": [...] } // 返回订单信息供商家二次确认
    }
    ```
*   **逻辑：** 校验码正确性 -> 订单状态变更为 `4 (已完成)` -> 记录核销时间。

### 4.4 店铺状态设置
*   **Method：** `POST /admin/shop/config`
*   **请求参数：**
    ```json
    {
      "is_open": 1, // 1营业 0打烊
      "open_time": "09:00",
      "close_time": "22:00"
    }
    ```

---

## 5. 💡 补充说明 (给开发者的Tips)

1.  **支付回调 (Webhook)：**
    *   需要预留一个 `POST /payment/notify` 接口，供微信服务器回调。
    *   **重要：** 只有收到微信的回调通知，才将订单状态从 `0 (待支付)` 修改为 `1 (待接单)` 或 `2 (待自提)`。不要仅依赖前端跳转。

2.  **轮询与Socket：**
    *   商家端为了实现“新订单语音播报”，建议使用 **WebSocket** 连接，或者每隔 30秒 **轮询** 一次 `/admin/order/list?status=pending` 接口。

3.  **并发锁：**
    *   在 `verify` (核销) 接口，要注意防止手抖点击两次导致报错，建议后端加锁或做幂等处理。
