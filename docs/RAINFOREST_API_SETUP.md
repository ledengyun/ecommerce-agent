# Rainforest API 注册与配置指南

## 📝 注册步骤

### 第 1 步：访问官网

打开浏览器访问：
**https://www.rainforestapi.com**

### 第 2 步：注册账号

1. 点击右上角 **"Sign Up"** 或 **"Get Started"**
2. 选择注册方式：
   - 邮箱注册（推荐）
   - Google 账号登录
   - GitHub 账号登录

### 第 3 步：验证邮箱

- 查收验证邮件
- 点击验证链接激活账号

### 第 4 步：获取 API 密钥

1. 登录后进入 **Dashboard**
2. 点击左侧菜单 **"API Keys"**
3. 复制您的 API 密钥（格式类似：`a1b2c3d4e5f6g7h8i9j0`）

### 第 5 步：免费试用

- 新账号自动获得 **100 次免费请求**
- 无需绑定信用卡
- 有效期 30 天

---

## 🔑 配置 API 密钥

### 方式一：临时设置（当前终端有效）

```bash
export RAINFOREST_API_KEY="your_api_key_here"
```

### 方式二：永久设置（推荐）

编辑 `~/.bashrc` 或 `~/.zshrc`：

```bash
echo 'export RAINFOREST_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 方式三：项目配置文件

创建 `.env` 文件：

```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent
cat > .env << EOF
RAINFOREST_API_KEY=your_api_key_here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=EcommerceAgent2026!
DB_NAME=ecommerce_agent
EOF
```

---

## 🧪 测试 API

### 测试脚本

```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent

# 设置 API 密钥
export RAINFOREST_API_KEY="your_api_key_here"

# 运行测试
python3 src/temu_scraper_api.py
```

### 预期输出

```
============================================================
Temu 商品采集测试
============================================================

✅ 采集完成：10 个商品

前 3 个商品示例:

1. Home Goods Storage Basket - $12.99
   价格：12.99 USD
   评分：4.5

2. Kitchen Organizer Set - $24.99
   价格：24.99 USD
   评分：4.7
```

---

## 💰 价格方案

| 方案 | 价格/月 | 请求次数 | 适合场景 |
|------|---------|----------|----------|
| **免费试用** | $0 | 100 次 | 测试/评估 |
| **Starter** | $75 | 500 次 | 小规模采集 |
| **Growth** | $195 | 1,500 次 | 中等规模 |
| **Professional** | $395 | 4,000 次 | 大规模采集 |

---

## ⚠️ 重要提示

### Temu 支持说明

Rainforest API 主要支持以下电商平台：
- ✅ Amazon（最完善）
- ✅ Google Shopping
- ✅ Walmart
- ✅ Target
- ⚠️ **Temu** - 需要确认支持情况

**如果 Rainforest 不支持 Temu，备选方案：**

1. **ScraperAPI** - 通用爬虫 API
   - 网址：https://www.scraperapi.com
   - 免费试用：5000 次 API 调用
   - 可以爬取任意网站（包括 Temu）

2. **Bright Data** - 专业电商爬虫
   - 网址：https://brightdata.com
   - 有 Temu 专用爬虫
   - 免费试用可用

3. **Oxylabs** - 电商爬虫
   - 网址：https://oxylabs.io
   - 支持 Temu

---

## 🔧 使用示例

### 1. 采集 Temu 商品

```python
from src.temu_scraper_api import TemuScraper

scraper = TemuScraper(api_service='rainforest', api_key='YOUR_KEY')
products = scraper.search_products('home goods', limit=20)

print(f'采集到 {len(products)} 个商品')
```

### 2. 多平台采集

```python
from src.data_collector import DataCollector

collector = DataCollector()
results = collector.collect(
    keyword='home goods',
    platforms=['1688', 'temu'],
    limit_per_platform=20,
    output_file='data/combined_products.json'
)
```

### 3. 自动导入数据库

```bash
# 采集的数据会自动保存到 data/ 目录
# 启动自动导入服务
python3 database/auto_import.py --mode watch
```

---

## 📞 获取帮助

- **官方文档**: https://docs.rainforestapi.com
- **API 参考**: https://www.rainforestapi.com/docs
- **支持邮箱**: support@rainforestapi.com

---

## 📋 检查清单

- [ ] 访问 rainforestapi.com 注册账号
- [ ] 验证邮箱
- [ ] 获取 API 密钥
- [ ] 设置环境变量
- [ ] 运行测试脚本
- [ ] 确认 Temu 支持情况
- [ ] 如不支持，考虑备选方案（ScraperAPI/Bright Data）
