# Temu 数据采集 - 快速开始

## 🎯 当前状态

### ✅ 已完成
- [x] Rainforest API 密钥配置 (4459EA5ABF49448BAA6829CE5CE1587C)
- [x] 测试确认：Rainforest **不支持** Temu
- [x] 创建 ScraperAPI 采集方案
- [x] 自动导入数据库功能

### ⚠️ 需要操作
- [ ] 注册 ScraperAPI 获取密钥（5 分钟）
- [ ] 运行测试脚本验证采集

---

## 🚀 5 分钟快速开始

### 第 1 步：注册 ScraperAPI（2 分钟）

1. 访问：https://www.scraperapi.com
2. 点击 **"Get Started"** 或 **"Sign Up"**
3. 使用邮箱或 Google 账号注册
4. 验证邮箱
5. 进入 Dashboard 复制 API 密钥

**免费额度：5000 次 API 调用**（无需信用卡）

### 第 2 步：运行测试脚本（3 分钟）

```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent
./scripts/test_temu_collection.sh
```

脚本会自动：
- 检查依赖
- 提示输入 API 密钥
- 测试采集 Temu 数据
- 可选导入数据库

### 第 3 步：查看结果

```bash
# 查看采集的数据
cat data/temu_products_*.json | head -50

# 查看数据库
mysql -u root -p'EcommerceAgent2026!' -e "SELECT title, supplier_price, profit_margin FROM ecommerce_agent.products ORDER BY id DESC LIMIT 10;"
```

---

## 📁 项目文件结构

```
ecommerce-agent/
├── src/
│   ├── temu_scraper_api.py       # Rainforest API 采集器（不支持 Temu）
│   ├── temu_scraper_direct.py    # ScraperAPI 直接采集器 ✅ 推荐
│   └── data_collector.py         # 统一数据采集器
├── database/
│   ├── auto_import.py            # 自动导入数据库 ✅
│   └── init.sql                  # 数据库表结构
├── scripts/
│   ├── setup_api_key.sh          # API 密钥配置脚本
│   └── test_temu_collection.sh   # Temu 采集测试脚本 ✅
├── docs/
│   ├── TEMU_DATA_COLLECTION_STRATEGY.md  # 完整策略文档
│   ├── RAINFOREST_API_SETUP.md           # Rainforest 配置指南
│   └── temu_api_setup.html               # 可视化配置页面
└── data/
    ├── incoming/                 # 自动导入监听目录
    └── processed/                # 已处理文件目录
```

---

## 💡 使用场景

### 场景 1: 单次采集

```bash
# 配置密钥
export SCRAPERAPI_API_KEY="your_key"

# 采集
python3 src/temu_scraper_direct.py
```

### 场景 2: 多平台对比

```python
from src.data_collector import DataCollector

collector = DataCollector()
results = collector.collect(
    keyword='home goods',
    platforms=['1688', 'temu'],  # 1688 + Temu
    limit_per_platform=20
)

# 价格对比
comparison = collector.compare_prices()
print(comparison)
```

### 场景 3: 自动化工作流

```bash
# 1. 启动自动导入服务（后台运行）
nohup python3 database/auto_import.py --mode watch > /var/log/auto_import.log 2>&1 &

# 2. 采集数据（自动导入数据库）
python3 src/temu_scraper_direct.py

# 3. 查看结果
mysql -u root -p -e "SELECT * FROM ecommerce_agent.products ORDER BY created_at DESC LIMIT 10;"
```

---

## 🔑 API 密钥管理

### 当前配置

| 服务 | API 密钥 | 状态 | 余额 |
|------|---------|------|------|
| Rainforest API | 4459EA5ABF... | ✅ 有效 | 92 次 |
| ScraperAPI | 未配置 | ⏳ 待注册 | 5000 次免费 |

### 配置命令

```bash
# 临时配置（当前终端）
export SCRAPERAPI_API_KEY="your_key"

# 永久配置
echo 'export SCRAPERAPI_API_KEY="your_key"' >> ~/.bashrc
source ~/.bashrc
```

---

## 📊 数据流程图

```
┌─────────────────┐
│  ScraperAPI     │
│  (代理服务)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Temu.com       │
│  (目标网站)     │
└────────┬────────┘
         │
         ↓ HTML
┌─────────────────┐
│  temu_scraper_  │
│  direct.py      │
│  (解析器)       │
└────────┬────────┘
         │
         ↓ JSON
┌─────────────────┐
│  data/          │
│  temu_products_ │
│  *.json         │
└────────┬────────┘
         │
         ↓ 自动监听
┌─────────────────┐
│  auto_import.py │
│  (导入器)       │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  MySQL          │
│  products 表    │
└─────────────────┘
```

---

## ⚠️ 常见问题

### Q1: 为什么 Rainforest API 不能用？

**A:** Rainforest API 主要支持 Amazon、Walmart 等平台，`temu.com` 不在其支持列表中。

**解决方案:** 使用 ScraperAPI（通用爬虫）或 Bright Data（有 Temu 专用爬虫）。

### Q2: ScraperAPI 免费额度够用吗？

**A:** 5000 次免费额度足够：
- 测试：约 10-20 次
- 小规模采集（每天 10 次）：可用 1 年
- 中规模采集（每天 100 次）：可用 50 天

### Q3: 采集失败怎么办？

**检查清单:**
- [ ] API 密钥是否正确
- [ ] 网络连接是否正常
- [ ] BeautifulSoup 是否安装：`pip install beautifulsoup4`
- [ ] Temu 网站是否可访问

### Q4: 数据没有自动导入数据库？

**检查:**
1. 自动导入服务是否运行
2. 文件是否放在 `data/incoming/` 目录
3. 查看日志：`tail -f /var/log/auto_import.log`

---

## 📞 获取帮助

### 文档
- 完整策略：`docs/TEMU_DATA_COLLECTION_STRATEGY.md`
- Rainforest 配置：`docs/RAINFOREST_API_SETUP.md`

### 测试命令
```bash
# 测试采集
./scripts/test_temu_collection.sh

# 测试 API 连接
python3 src/temu_scraper_direct.py

# 测试数据库导入
python3 database/auto_import.py --mode once --file data/temu_products.json
```

---

## ✅ 下一步

1. **立即注册 ScraperAPI** → https://www.scraperapi.com
2. **运行测试脚本** → `./scripts/test_temu_collection.sh`
3. **查看采集结果** → `cat data/temu_products_*.json`

---

**需要帮助？** 运行以下命令查看详细文档：

```bash
cat docs/TEMU_DATA_COLLECTION_STRATEGY.md
```
