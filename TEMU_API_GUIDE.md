# 🛒 Temu 数据采集 - 第三方 API 方案

## 📋 方案说明

使用第三方 API 服务采集 Temu 商品数据，绕过反爬机制。

### 支持的 API 服务

| 服务商 | 免费额度 | 价格 | 推荐度 |
|--------|----------|------|--------|
| **Rainforest API** | 100 次/月 | $75/1000 次 | ⭐⭐⭐⭐⭐ |
| **ScraperAPI** | 1000 次/月 | $29/月 | ⭐⭐⭐⭐ |
| **Oxylabs** | 试用 | $99/月起 | ⭐⭐⭐⭐ |
| **Bright Data** | 试用 | $15/GB | ⭐⭐⭐⭐ |

---

## 🚀 快速开始

### Step 1: 注册 API 账号

**推荐：Rainforest API**
1. 访问：https://www.rainforestapi.com
2. 注册免费账号
3. 获取 API Key
4. 免费额度：100 次/月

### Step 2: 配置 API 密钥

**方式 1：环境变量（推荐）**
```bash
export RAINFOREST_API_KEY=your_api_key_here
```

**方式 2：配置文件**
编辑 `config/temu_api.yaml`：
```yaml
RAINFOREST_API_KEY: your_api_key_here
DEFAULT_API_SERVICE: rainforest
```

### Step 3: 测试采集

```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent
python3 src/temu_scraper_api.py
```

---

## 💡 使用方式

### 方式 1：命令行运行

```bash
# 使用默认配置
python3 src/temu_scraper_api.py

# 指定关键词和数量
python3 -c "
from src.temu_scraper_api import search_temu_products
products = search_temu_products('home goods', limit=20)
print(f'采集到 {len(products)} 个商品')
"
```

### 方式 2：Python 代码调用

```python
from src.temu_scraper_api import TemuScraper

# 创建采集器
scraper = TemuScraper(
    api_service='rainforest',
    api_key='your_api_key'
)

# 搜索商品
products = scraper.search_products('kitchen gadgets', limit=20)

# 保存结果
scraper.save_products(products, 'data/temu_products.json')

print(f'采集到 {len(products)} 个商品')
```

### 方式 3：集成到现有系统

```python
# 在 ecommerce-agent 中使用
from src.temu_scraper_api import search_temu_products

# 采集 Temu 商品
temu_products = search_temu_products(
    keyword='home decor',
    limit=30,
    api_service='rainforest'
)

# 导入数据库（复用现有导入脚本）
# ...
```

---

## 📊 API 对比

### Rainforest API ⭐ 推荐

**优点：**
- ✅ 专门支持电商网站
- ✅ 数据结构化好
- ✅ 稳定性高
- ✅ 有免费额度

**缺点：**
- ❌ 价格较高
- ❌ Temu 支持可能有限

**使用示例：**
```python
scraper = TemuScraper(api_service='rainforest', api_key='xxx')
products = scraper.search_products('electronics', limit=20)
```

### ScraperAPI

**优点：**
- ✅ 免费额度多（1000 次/月）
- ✅ 支持 JavaScript 渲染
- ✅ 价格便宜

**缺点：**
- ❌ 需要自己解析 HTML
- ❌ 稳定性一般

**使用示例：**
```python
scraper = TemuScraper(api_service='scraperapi', api_key='xxx')
products = scraper.search_products('fashion', limit=20)
```

### Oxylabs

**优点：**
- ✅ 专业电商数据采集
- ✅ 成功率高
- ✅ 速度快

**缺点：**
- ❌ 需要付费
- ❌ 配置复杂

### Bright Data

**优点：**
- ✅ 最大的代理网络
- ✅ 支持多种采集方式
- ✅ 数据质量好

**缺点：**
- ❌ 按流量计费
- ❌ 配置复杂

---

## 🔧 高级配置

### 自定义 API 参数

```python
from src.temu_scraper_api import TemuScraper

scraper = TemuScraper(api_service='rainforest', api_key='xxx')

# 自定义搜索参数
params = {
    'search_term': 'home goods',
    'sort_by': 'price_low_to_high',  # 按价格排序
    'page': 1,  # 页码
}

products = scraper.search_products(**params)
```

### 批量采集

```python
keywords = ['home goods', 'kitchen', 'electronics', 'fashion']

all_products = []
for keyword in keywords:
    products = search_temu_products(keyword, limit=20)
    all_products.extend(products)
    print(f'{keyword}: {len(products)} 个商品')

print(f'总计：{len(all_products)} 个商品')
```

### 错误处理

```python
from src.temu_scraper_api import TemuScraper

scraper = TemuScraper(api_service='rainforest', api_key='xxx')

try:
    products = scraper.search_products('electronics', limit=20)
    if products:
        scraper.save_products(products)
    else:
        print("未采集到商品")
except Exception as e:
    print(f"采集失败：{e}")
```

---

## 📁 数据格式

### 采集结果示例

```json
[
  {
    "title": "LED Desk Lamp with USB Charging Port",
    "price": 15.99,
    "currency": "USD",
    "rating": 4.5,
    "ratings_total": 1234,
    "image": "https://img.temu.com/xxx.jpg",
    "url": "https://www.temu.com/xxx.html",
    "position": 1,
    "is_prime": false,
    "platform": "Temu",
    "extracted_at": "2026-03-12T17:15:00Z"
  }
]
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `title` | 商品标题 |
| `price` | 价格 |
| `currency` | 货币单位 |
| `rating` | 评分 |
| `ratings_total` | 评价数量 |
| `image` | 图片 URL |
| `url` | 商品链接 |
| `position` | 搜索排名 |
| `platform` | 平台（Temu） |
| `extracted_at` | 提取时间 |

---

## 💰 成本估算

### Rainforest API

**免费额度：**
- 100 次/月
- 每次最多 20 个商品
- 总计：2000 个商品/月

**付费方案：**
- $75/1000 次
- 每次最多 20 个商品
- 总计：20,000 个商品
- 单价：$0.00375/商品

### ScraperAPI

**免费额度：**
- 1000 次/月
- 每次无限制
- 总计：约 20,000 个商品/月

**付费方案：**
- $29/月（5000 次）
- 总计：约 100,000 个商品
- 单价：$0.00029/商品

---

## 🐛 故障排查

### Q1: API 密钥无效

**解决：**
```bash
# 检查环境变量
echo $RAINFOREST_API_KEY

# 重新设置
export RAINFOREST_API_KEY=your_key
```

### Q2: 采集结果为空

**原因：**
- API 密钥无效
- 关键词无结果
- API 服务限制

**解决：**
1. 检查 API 密钥
2. 更换关键词
3. 查看 API 服务商状态

### Q3: 请求超时

**解决：**
```python
# 增加超时时间
scraper = TemuScraper(api_service='rainforest', api_key='xxx')
# 修改源码中的 timeout 参数
```

### Q4: 数据格式不对

**解决：**
- 检查 API 服务商文档
- 查看返回的原始数据
- 调整解析逻辑

---

## 📝 最佳实践

### 1. 使用免费额度开始

先用免费额度测试，确认数据质量后再付费。

### 2. 多 API 服务备份

配置多个 API 服务，一个失败自动切换另一个。

### 3. 缓存采集结果

```python
import json
from pathlib import Path

cache_file = Path('data/temu_cache.json')

if cache_file.exists():
    # 使用缓存
    products = json.load(open(cache_file))
else:
    # 采集新数据
    products = search_temu_products('keyword')
    json.dump(products, open(cache_file, 'w'))
```

### 4. 定期更新数据

设置定时任务，定期更新商品数据：

```bash
# 每天凌晨 2 点采集
0 2 * * * cd /path/to/ecommerce-agent && python3 src/temu_scraper_api.py
```

---

## 🎯 与 1688 结合使用

### 选品流程

```
1. Temu 采集爆款
   ↓
2. 分析热销趋势
   ↓
3. 1688 寻找同款货源
   ↓
4. 利润分析
   ↓
5. 上架销售
```

### 数据对比

```python
# 采集 Temu 数据
temu_products = search_temu_products('home goods', limit=20)

# 采集 1688 数据
# ... (使用现有 1688 采集脚本)

# 对比价格
for temu_item in temu_products:
    # 在 1688 找同款
    # 计算利润空间
    pass
```

---

## 📞 API 服务商链接

- **Rainforest API**: https://www.rainforestapi.com
- **ScraperAPI**: https://www.scraperapi.com
- **Oxylabs**: https://oxylabs.io
- **Bright Data**: https://brightdata.com

---

**现在注册 API，开始采集 Temu 商品数据！** 🚀
