# 后端服务架构文档

**版本**: 2.0.0  
**更新时间**: 2026-03-13

---

## 📐 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (前端)                       │
│              Web 页面 / 移动端 / 第三方调用               │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────┐
│                   API Layer (API 接口层)                 │
│  ├─ amazon_api.py    - Amazon 采集 API                   │
│  ├─ temu_api.py      - Temu 采集 API                     │
│  ├─ product_api.py   - 商品管理 API                      │
│  └─ analysis_api.py  - 分析 API                          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Service Layer (业务逻辑层)                │
│  ├─ amazon_service.py - Amazon 采集业务逻辑              │
│  ├─ temu_service.py   - Temu 采集业务逻辑               │
│  ├─ product_service.py - 商品管理业务逻辑               │
│  └─ analysis_service.py - 分析业务逻辑                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  DAO Layer (数据访问层)                  │
│  ├─ product_dao.py   - 产品数据访问                      │
│  ├─ task_dao.py      - 任务数据访问                      │
│  └─ user_dao.py      - 用户数据访问                      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Database (MySQL 数据库)                   │
│  └─ ecommerce_agent.products                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               Utils Layer (工具层)                       │
│  ├─ db_utils.py       - 数据库工具                       │
│  ├─ http_utils.py     - HTTP 请求工具                    │
│  └─ common_utils.py   - 通用工具                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Config Layer (配置层)                       │
│  └─ settings.py       - 所有配置信息                     │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 目录结构

```
backend/
├── main.py                 # 启动文件 ✅
├── config/
│   ├── __init__.py
│   └── settings.py         # 配置文件 ✅
├── api/
│   ├── __init__.py
│   └── amazon_api.py       # Amazon API ✅
├── service/
│   ├── __init__.py
│   └── amazon_service.py   # Amazon 服务 ✅
├── dao/
│   ├── __init__.py
│   └── product_dao.py      # 产品 DAO ✅
├── utils/
│   ├── __init__.py
│   ├── db_utils.py         # 数据库工具 ✅
│   ├── http_utils.py       # HTTP 工具 ✅
│   └── common_utils.py     # 通用工具 ✅
├── logs/                   # 日志目录
└── requirements.txt        # 依赖
```

---

## 🔧 各层职责

### 1. 配置层 (config)

**文件**: `config/settings.py`

**职责**:
- 数据库配置
- API 密钥管理
- 业务参数配置
- 功能开关控制

**示例**:
```python
from config import DB_CONFIG, RAINFOREST_CONFIG

db_host = DB_CONFIG['host']
api_key = RAINFOREST_CONFIG['api_key']
```

---

### 2. 工具层 (utils)

**文件**:
- `db_utils.py` - 数据库连接管理
- `http_utils.py` - HTTP 请求封装
- `common_utils.py` - 通用工具函数

**职责**:
- 数据库连接池
- HTTP 客户端（带重试）
- 数据转换、计算
- 第三方 API 客户端

**示例**:
```python
from utils import get_db, rainforest_client, calculate_profit

# 数据库操作
db = get_db()
products = db.fetch_all("SELECT * FROM products")

# API 调用
result = rainforest_client.search_products('home goods')

# 利润计算
profit = calculate_profit(10.0)
```

---

### 3. 数据访问层 (DAO)

**文件**: `dao/product_dao.py`

**职责**:
- 直接操作数据库
- CRUD 操作
- SQL 语句封装
- 数据映射

**示例**:
```python
from dao import product_dao

# 插入商品
product_dao.insert_product(product_data)

# 查询商品
products = product_dao.get_products(limit=20)

# 统计
stats = product_dao.get_stats()
```

---

### 4. 业务逻辑层 (Service)

**文件**: `service/amazon_service.py`

**职责**:
- 业务逻辑实现
- 调用 DAO 层
- 调用外部 API
- 数据处理和转换
- 事务管理

**示例**:
```python
from service import amazon_service

# 采集商品
result = amazon_service.search_products('home goods', limit=20)

# 导入数据库
import_result = amazon_service.import_products(result['products'])
```

---

### 5. API 接口层 (API)

**文件**: `api/amazon_api.py`

**职责**:
- 接收 HTTP 请求
- 参数验证
- 调用 Service 层
- 返回 HTTP 响应
- 错误处理

**示例**:
```python
@router.post("/collect")
async def collect_amazon(request: AmazonCollectRequest):
    amazon_service = get_amazon_service()
    result = amazon_service.search_products(request.keyword)
    return result
```

---

### 6. 启动文件 (main.py)

**职责**:
- 应用初始化
- 中间件配置
- 路由注册
- 生命周期事件
- 错误处理

---

## 🔄 数据流示例

### Amazon 采集流程

```
1. 前端请求
   POST /api/amazon/collect
   { "keyword": "home goods", "limit": 20 }

   ↓

2. API 层 (amazon_api.py)
   - 验证参数
   - 调用 Service

   ↓

3. Service 层 (amazon_service.py)
   - 调用 Rainforest API
   - 解析数据
   - 计算利润

   ↓

4. 工具层 (http_utils.py)
   - 发送 HTTP 请求
   - 处理重试

   ↓

5. Rainforest API
   - 返回商品数据

   ↓

6. Service 层
   - 标准化数据
   - 调用 DAO 导入

   ↓

7. DAO 层 (product_dao.py)
   - 批量插入数据库

   ↓

8. 返回结果
   {
     "success": true,
     "total_products": 20,
     "imported": 20
   }
```

---

## 📊 数据库表结构

### products 表

```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    price VARCHAR(50),
    supplier_price DECIMAL(10,2),
    retail_price DECIMAL(10,2),
    profit_margin DECIMAL(5,4),
    image_url TEXT,
    source_url TEXT,
    sales VARCHAR(50),
    rating DECIMAL(3,2),
    recommend BOOLEAN,
    platform VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## 🔐 配置管理

### 环境变量

```bash
# 数据库
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=EcommerceAgent2026!
DB_NAME=ecommerce_agent

# API 密钥
RAINFOREST_API_KEY=4459EA5ABF49448BAA6829CE5CE1587C
SCRAPERAPI_API_KEY=a03095a3ea309111095c445b10cc9018

# 业务配置
RETAIL_PRICE_MULTIPLIER=3.5
SHIPPING_COST=5.0
MIN_PROFIT_MARGIN=0.3

# 服务配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false
```

### .env 文件

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑配置
vim .env
```

---

## 🚀 启动服务

### 开发模式

```bash
cd backend
python3 main.py
```

或使用 uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📖 API 文档

启动服务后访问:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧪 测试

### API 测试

```bash
# 测试 Amazon 采集
curl -X POST http://localhost:8000/api/amazon/collect \
  -H "Content-Type: application/json" \
  -d '{"keyword": "home goods", "limit": 5}'
```

### Python 测试

```python
from service import amazon_service

result = amazon_service.search_products('home goods')
assert result['success'] == True
assert len(result['products']) > 0
```

---

## 📝 扩展指南

### 添加新的 API

1. 在 `api/` 目录创建文件
2. 定义路由
3. 在 `main.py` 注册

### 添加新的 Service

1. 在 `service/` 目录创建文件
2. 实现业务逻辑
3. 调用 DAO 和工具

### 添加新的 DAO

1. 在 `dao/` 目录创建文件
2. 实现 SQL 操作
3. 使用 `get_db()` 获取连接

---

## ✅ 优势

### 代码组织
- ✅ 清晰的职责分离
- ✅ 易于理解和维护
- ✅ 便于团队协作

### 可测试性
- ✅ 各层独立测试
- ✅ Mock 容易
- ✅ 单元测试友好

### 可扩展性
- ✅ 添加新功能简单
- ✅ 不影响现有代码
- ✅ 支持模块替换

### 可维护性
- ✅ 配置集中管理
- ✅ 日志统一管理
- ✅ 错误统一处理

---

## 📞 相关文档

- `AMAZON_API_GUIDE.md` - Amazon API 使用指南
- `AMAZON_FRONTEND_INTEGRATION.md` - 前端集成文档
- `/docs/` - 更多文档
