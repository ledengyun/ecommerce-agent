# Temu 数据采集策略

## 📊 测试结果总结

### Rainforest API ❌
- **状态**: 不支持 Temu
- **API 密钥**: 4459EA5ABF49448BAA6829CE5CE1587C (有效，92 次余额)
- **问题**: `temu.com` 不在支持列表中
- **用途**: 可用于 Amazon、Walmart 等其他平台

### ScraperAPI ✅ (推荐)
- **状态**: 支持任意网站，包括 Temu
- **免费额度**: 5000 次 API 调用
- **注册**: https://www.scraperapi.com
- **优势**: JavaScript 渲染、自动代理轮换

### Bright Data ✅
- **状态**: 有 Temu 专用爬虫
- **免费试用**: 可用
- **注册**: https://brightdata.com

---

## 🚀 推荐方案：ScraperAPI

### 第 1 步：注册获取密钥

访问 https://www.scraperapi.com 注册账号

**免费试用：**
- 5000 次 API 调用
- 无需信用卡
- 足够测试和小规模采集

### 第 2 步：配置密钥

```bash
export SCRAPERAPI_API_KEY="your_api_key_here"
```

### 第 3 步：测试采集

```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent
python3 src/temu_scraper_direct.py
```

### 第 4 步：集成到工作流

```python
from src.temu_scraper_direct import search_temu_direct

# 采集 Temu 数据
products = search_temu_direct('home goods', limit=20)

# 自动导入数据库
from database.auto_import import import_products_to_db
result = import_products_to_db(products, platform='temu')
print(f"导入成功：{result['imported']} 个商品")
```

---

## 📋 完整工作流程

```
┌─────────────────────────────────────────────────────────┐
│  1. 获取 ScraperAPI 密钥                                  │
│     └─→ https://www.scraperapi.com                      │
│     └─→ 注册 → 获取 5000 次免费请求                        │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  2. 配置环境变量                                         │
│     └─→ export SCRAPERAPI_API_KEY="xxx"                 │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  3. 采集 Temu 数据                                        │
│     └─→ python3 src/temu_scraper_direct.py             │
│     └─→ 数据保存到 data/temu_products_*.json           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  4. 自动导入数据库                                       │
│     └─→ python3 database/auto_import.py --mode watch   │
│     └─→ 数据写入 products 表                             │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 代码示例

### 示例 1: 简单采集

```python
from src.temu_scraper_direct import search_temu_direct

products = search_temu_direct('kitchen gadgets', limit=20)
print(f"采集到 {len(products)} 个商品")
```

### 示例 2: 多平台采集

```python
from src.data_collector import DataCollector

collector = DataCollector()
results = collector.collect(
    keyword='home goods',
    platforms=['1688', 'temu'],  # 1688 + Temu
    limit_per_platform=20,
    output_file='data/combined_products.json'
)

# 显示结果
for platform, products in results.items():
    print(f"{platform}: {len(products)} 个商品")
```

### 示例 3: 自动导入数据库

```python
from src.temu_scraper_direct import TemuDirectScraper
from database.auto_import import import_products_to_db

# 采集
scraper = TemuDirectScraper(api_key='your_key')
products = scraper.search_products('home goods', limit=50)

# 导入
result = import_products_to_db(products, platform='temu')
print(f"导入成功：{result['imported']} 个商品")
print(f"推荐商品：{result['recommended']} 个")
```

---

## 🔧 依赖安装

```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent

# 安装 BeautifulSoup4（HTML 解析）
pip install beautifulsoup4

# 安装 requests（HTTP 请求）
pip install requests

# 安装 pymysql（数据库连接）
pip install pymysql
```

---

## ⚠️ 注意事项

### 1. Temu 反爬虫

Temu 有较强的反爬虫措施：
- JavaScript 渲染
- 动态加载
- IP 封禁

**解决方案**: 使用 ScraperAPI 等代理服务

### 2. 页面结构变化

Temu 经常更新页面结构，选择器可能失效：
- 定期检查采集脚本
- 使用智能匹配备用方案
- 更新 `_parse_html` 方法中的选择器

### 3. 采集频率限制

- ScraperAPI 免费版：5000 次/月
- 建议合理控制采集频率
- 批量采集时注意配额

---

## 📊 数据格式

采集的商品数据格式：

```json
{
  "title": "Kitchen Storage Organizer",
  "price": 12.99,
  "currency": "USD",
  "rating": 4.5,
  "sales": "1000+ sold",
  "image": "https://...",
  "url": "https://www.temu.com/...",
  "platform": "Temu",
  "extracted_at": "2026-03-13T09:00:00"
}
```

自动导入数据库时会计算：
- `supplier_price`: 供货价
- `retail_price`: 建议零售价 (供货价 × 3.5)
- `profit_margin`: 利润率
- `recommend`: 是否推荐 (利润率 ≥ 30%)

---

## 🎯 最佳实践

### 1. 关键词选择

选择具体、有商业价值的关键词：
- ✅ `kitchen organizer`
- ✅ `home storage`
- ✅ `bathroom accessories`
- ❌ `stuff` (太宽泛)

### 2. 采集时间

- 避开高峰期（美国工作时间）
- 建议：北京时间凌晨 2-6 点

### 3. 数据更新

- 定期更新采集数据（每周）
- 使用自动导入监听模式
- 保留历史数据用于价格趋势分析

### 4. 利润计算

默认配置：
- 零售价倍率：3.5x
- 运费估算：$5
- 最低利润率：30%

可根据实际情况调整 `database/auto_import.py` 中的 `CONFIG`。

---

## 📞 获取帮助

### ScraperAPI
- 官网：https://www.scraperapi.com
- 文档：https://www.scraperapi.com/documentation
- 支持：support@scraperapi.com

### 项目问题
- 查看日志：`tail -f /var/log/auto_import.log`
- 测试连接：`python3 src/temu_scraper_direct.py`

---

## ✅ 检查清单

- [ ] 注册 ScraperAPI 获取密钥
- [ ] 安装依赖：`pip install beautifulsoup4 requests pymysql`
- [ ] 配置环境变量：`export SCRAPERAPI_API_KEY="xxx"`
- [ ] 测试采集：`python3 src/temu_scraper_direct.py`
- [ ] 启动自动导入：`python3 database/auto_import.py --mode watch`
- [ ] 验证数据库：`mysql -u root -p -e "SELECT * FROM ecommerce_agent.products LIMIT 5"`
