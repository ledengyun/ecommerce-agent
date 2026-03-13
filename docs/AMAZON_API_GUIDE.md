# 亚马逊采集 API 使用指南

## 📋 概述

提供亚马逊商品采集的后端 API 接口，支持前端调用。

**API 密钥**: `4459EA5ABF49448BAA6829CE5CE1587C` (Rainforest API)  
**当前余额**: 91 次请求

---

## 🚀 API 端点

### 1. POST /api/amazon/collect

采集亚马逊商品

**请求**:
```json
{
  "keyword": "home goods",
  "limit": 20,
  "auto_import": true
}
```

**参数说明**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| keyword | string | ✅ 是 | - | 搜索关键词 |
| limit | integer | ❌ 否 | 20 | 采集数量 (1-100) |
| auto_import | boolean | ❌ 否 | true | 是否自动导入数据库 |

**响应**:
```json
{
  "success": true,
  "message": "成功采集 20 个亚马逊商品",
  "keyword": "home goods",
  "total_products": 20,
  "products": [
    {
      "title": "商品标题",
      "price": 17.99,
      "currency": "USD",
      "rating": 4.6,
      "ratings_total": 2744,
      "image": "https://...",
      "url": "https://amazon.com/...",
      "is_prime": false,
      "platform": "Amazon",
      "asin": "B0D7979744"
    }
  ],
  "import_result": {
    "success": true,
    "imported": 20,
    "recommended": 15,
    "total_in_db": 190
  }
}
```

---

### 2. GET /api/amazon/status

获取采集器状态

**响应**:
```json
{
  "status": "online",
  "api_configured": true,
  "api_key_prefix": "4459EA5ABF",
  "supported_domains": [
    "amazon.com",
    "amazon.co.uk",
    "amazon.de",
    "amazon.fr",
    "amazon.co.jp",
    "amazon.ca",
    "amazon.com.au"
  ]
}
```

---

## 💻 前端调用示例

### JavaScript (Fetch)

```javascript
async function collectAmazon(keyword, limit = 20) {
  const response = await fetch('/api/amazon/collect', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      keyword: keyword,
      limit: limit,
      auto_import: true
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    console.log(`采集成功：${data.total_products} 个商品`);
    console.log(data.products);
  } else {
    console.error('采集失败:', data.message);
  }
}

// 使用示例
collectAmazon('kitchen gadgets', 20);
```

### Python (Requests)

```python
import requests

def collect_amazon(keyword, limit=20):
    response = requests.post(
        'http://localhost:8000/api/amazon/collect',
        json={
            'keyword': keyword,
            'limit': limit,
            'auto_import': True
        }
    )
    
    data = response.json()
    
    if data['success']:
        print(f"采集成功：{data['total_products']} 个商品")
        return data['products']
    else:
        print(f"采集失败：{data['message']}")
        return []

# 使用示例
products = collect_amazon('home goods')
```

---

## 🎨 前端页面

访问：`http://localhost:8000/amazon_collect.html`

**功能**:
- ✅ 输入关键词
- ✅ 设置采集数量
- ✅ 选择亚马逊站点
- ✅ 实时显示采集进度
- ✅ 展示商品列表
- ✅ 自动导入数据库

---

## 📊 数据库导入

采集的商品会自动导入到 `ecommerce_agent.products` 表

**导入字段**:
- title: 商品标题
- supplier_price: 价格 (USD)
- retail_price: 建议零售价 (自动计算)
- profit_margin: 利润率 (自动计算)
- recommend: 是否推荐 (自动判断)
- platform: 'Amazon'
- image_url: 商品图片
- source_url: 商品链接

**利润率计算**:
```python
retail_price = supplier_price * 3.5
estimated_cost = supplier_price + 5
profit = retail_price - estimated_cost
profit_margin = profit / retail_price
recommend = profit_margin >= 0.3
```

---

## 🔧 后端服务

### 启动服务

```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent/backend
python3 main.py
```

或使用 uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📝 使用场景

### 场景 1: 前端采集按钮

```html
<button onclick="collectAmazon()">采集亚马逊</button>

<script>
async function collectAmazon() {
  const keyword = document.getElementById('keyword').value;
  
  const response = await fetch('/api/amazon/collect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ keyword, limit: 20 })
  });
  
  const data = await response.json();
  
  if (data.success) {
    alert(`采集成功：${data.total_products} 个商品`);
  }
}
</script>
```

### 场景 2: 定时采集

```python
import schedule
import time

def daily_collection():
    """每日采集任务"""
    keywords = ['home goods', 'kitchen gadgets', 'storage']
    
    for keyword in keywords:
        collect_amazon(keyword, limit=10)
        time.sleep(2)  # 避免请求过快

# 每天早上 9 点执行
schedule.every().day.at("09:00").do(daily_collection)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 场景 3: 价格监控

```python
# 监控特定 ASIN 的价格变化
asin_list = ['B0D7979744', 'B0CVVVNB9L']

for asin in asin_list:
    details = scraper.get_product_details(asin)
    # 记录价格到数据库
    # 发送价格变化通知
```

---

## ⚠️ 注意事项

### API 限制

- **免费额度**: 100 次请求
- **当前余额**: 91 次
- **建议频率**: 每天 1-2 次采集

### 错误处理

```javascript
try {
  const response = await fetch('/api/amazon/collect', {
    method: 'POST',
    body: JSON.stringify({ keyword: 'test' })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  const data = await response.json();
  
} catch (error) {
  console.error('采集失败:', error.message);
}
```

### 性能优化

1. **批量采集**: 一次采集多个关键词
2. **缓存结果**: 避免重复采集相同关键词
3. **异步处理**: 使用后台任务处理大量采集

---

## 📞 故障排查

### 问题 1: API 返回 500 错误

**检查**:
- API 密钥是否正确
- 网络连接是否正常
- 查看后端日志

### 问题 2: 采集结果为空

**可能原因**:
- 关键词太具体
- 亚马逊站点选择错误
- API 余额不足

### 问题 3: 数据库导入失败

**检查**:
- 数据库连接是否正常
- 表结构是否正确
- 查看后端日志

---

## 📖 相关文档

- `AMAZON_COLLECTION_SUCCESS.md` - 采集测试报告
- `API_SETUP_SUMMARY.md` - API 配置总结
- `backend/main.py` - 后端源码
- `frontend/amazon_collect.html` - 前端页面

---

## ✅ 快速测试

```bash
# 1. 启动后端服务
cd /home/admin/.openclaw/workspace/ecommerce-agent/backend
python3 main.py

# 2. 访问前端页面
# http://localhost:8000/amazon_collect.html

# 3. 或使用 curl 测试
curl -X POST http://localhost:8000/api/amazon/collect \
  -H "Content-Type: application/json" \
  -d '{"keyword": "home goods", "limit": 5}'
```
