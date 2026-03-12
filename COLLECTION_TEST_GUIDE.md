# 🔗 前后端联动测试指南

## 📋 数据采集功能联动

### 前端界面

**访问地址**: http://localhost:8000

**默认显示**: "数据采集" 标签页

### 后端 API

**端点**: `POST /api/collect`

**请求格式**:
```json
{
  "keyword": "home goods",
  "platforms": ["1688", "temu"],
  "limit": 20
}
```

**响应格式**:
```json
{
  "success": true,
  "keyword": "home goods",
  "platforms": ["1688", "temu"],
  "results": {
    "1688": [],
    "temu": []
  }
}
```

---

## 🧪 测试步骤

### Step 1: 测试后端 API

```bash
# 测试 1688 采集
curl -X POST http://localhost:8000/api/collect \
  -H "Content-Type: application/json" \
  -d '{"keyword": "home goods", "platforms": ["1688"], "limit": 10}'

# 测试 Temu 采集（需要 API 密钥）
export RAINFOREST_API_KEY=your_key
curl -X POST http://localhost:8000/api/collect \
  -H "Content-Type: application/json" \
  -d '{"keyword": "home goods", "platforms": ["temu"], "limit": 10}'
```

### Step 2: 测试前端界面

1. **打开浏览器**: http://localhost:8000
2. **选择平台**: 点击 1688 或 Temu 卡片
3. **输入关键词**: 例如 "home goods"
4. **选择数量**: 20 个商品
5. **点击采集**: "🚀 开始采集" 按钮
6. **查看进度**: 实时显示采集状态
7. **查看结果**: 弹出提示框显示结果

---

## 📊 平台联动说明

### 1688（人工辅助）

**前端操作**:
1. 选择 1688 平台
2. 输入关键词
3. 点击"开始采集"

**后端处理**:
```python
# 返回提示信息
{
  "1688": []
}
```

**前端提示**:
```
ℹ️ 请使用脚本采集
1. 访问 1688.com
2. 搜索：home goods
3. 按 F12
4. 运行 scripts/extract_1688_auto.js
5. 保存 JSON 文件
```

**用户操作**:
1. 访问 1688.com
2. 搜索关键词
3. 运行提取脚本
4. 自动下载 JSON 文件
5. 文件保存到 `data/1688_products_时间戳.json`

---

### Temu（API 自动采集）

**前端操作**:
1. 选择 Temu 平台
2. 输入关键词
3. 点击"开始采集"

**后端处理**:
```python
# 调用 TemuScraper
from src.temu_scraper_api import TemuScraper

scraper = TemuScraper(api_service='rainforest', api_key=api_key)
products = scraper.search_products(keyword, limit)
```

**需要配置**:
```bash
export RAINFOREST_API_KEY=your_api_key
```

**前端显示**:
```
✅ 完成 (20 个)
```

---

## 🔧 故障排查

### Q1: API 返回 500 错误

**检查后端日志**:
```bash
journalctl -u ecommerce-agent -f
# 或
tail -f logs/backend.log
```

**常见错误**:
- `No module named 'src'` - 需要添加项目路径
- `No API key` - 需要配置 API 密钥

### Q2: 前端无响应

**检查浏览器 Console**:
```
F12 → Console → 查看错误信息
```

**常见错误**:
- `Network Error` - 后端服务未启动
- `404 Not Found` - API 路径错误

### Q3: 采集结果为空

**1688**:
- 正常现象，需要使用脚本采集

**Temu**:
- 检查 API 密钥：`echo $RAINFOREST_API_KEY`
- 检查网络连接
- 查看后端日志

---

## 📝 完整联动流程

```
用户操作（前端）
   ↓
1. 选择平台 + 输入关键词
   ↓
2. 点击"开始采集"
   ↓
3. 发送 POST /api/collect
   ↓
后端处理（FastAPI）
   ↓
4. 解析请求参数
   ↓
5. 调用 DataCollector
   ↓
6. 根据平台调用对应采集器
   ↓
7. 返回结果 JSON
   ↓
前端处理
   ↓
8. 接收响应
   ↓
9. 更新进度显示
   ↓
10. 弹出结果提示
   ↓
11. （可选）刷新商品列表
```

---

## 🎯 测试用例

### 用例 1: 1688 单平台采集

**请求**:
```json
{
  "keyword": "kitchen gadgets",
  "platforms": ["1688"],
  "limit": 10
}
```

**预期结果**:
- ✅ 前端显示采集完成
- ✅ 提示使用脚本采集
- ✅ 返回空数组（正常）

### 用例 2: Temu 单平台采集

**请求**:
```json
{
  "keyword": "home decor",
  "platforms": ["temu"],
  "limit": 20
}
```

**前提条件**:
```bash
export RAINFOREST_API_KEY=xxx
```

**预期结果**:
- ✅ 前端显示完成 (20 个)
- ✅ 保存 JSON 文件
- ✅ 返回商品列表

### 用例 3: 多平台同时采集

**请求**:
```json
{
  "keyword": "electronics",
  "platforms": ["1688", "temu"],
  "limit": 15
}
```

**预期结果**:
- ✅ 1688 提示使用脚本
- ✅ Temu 自动采集
- ✅ 显示各平台数量

---

## 📁 相关文件

### 前端
- `frontend/index.html` - 主页面（包含采集 UI）

### 后端
- `backend/main.py` - API 服务（包含 /api/collect）
- `src/data_collector.py` - 数据采集模块
- `src/temu_scraper_api.py` - Temu 采集器

### 脚本
- `scripts/extract_1688_auto.js` - 1688 提取脚本
- `test_collect_api.py` - API 测试脚本

---

## 🚀 快速测试命令

```bash
# 1. 启动后端
cd /home/admin/.openclaw/workspace/ecommerce-agent
python3 backend/main.py

# 2. 测试 API
python3 test_collect_api.py

# 3. 打开浏览器
# http://localhost:8000

# 4. 配置 Temu API（可选）
export RAINFOREST_API_KEY=your_key
```

---

**现在前后端已完全联动！** 🎉

访问 http://localhost:8000 测试采集功能。
