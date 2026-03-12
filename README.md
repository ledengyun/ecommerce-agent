# 🛒 电商选品上架 Agent

自动化的电商选品与 TikTok 上架系统，配备现代化 Web 控制台

## 🎉 新特性

### ✨ Web 控制台（新增）

现在可以通过浏览器访问美观的控制台界面：

```bash
# 启动服务
./start.sh

# 访问地址
http://localhost:8000
```

**功能特性:**
- 📊 实时统计仪表盘
- 📦 商品列表与推荐展示
- 🎯 一键执行利润分析
- 📋 实时日志查看

---

## 功能流程

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. 1688 选品    │ ──→ │  2. 利润分析    │ ──→ │  3. 素材下载    │ ──→ │  4. TikTok 上架  │
│  热销/爆款采集   │     │  供货价→零售价   │     │  商品轮播图      │     │  自动发布       │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 🚀 快速开始

### 方式 1: Web 控制台（推荐）

```bash
# 1. 启动服务
cd /home/admin/.openclaw/workspace/ecommerce-agent
./start.sh

# 2. 浏览器访问
# http://localhost:8000

# 3. 在控制台点击"开始分析"
```

### 方式 2: 命令行

```bash
# 1. 导入商品数据（从 1688）
# 运行 scripts/extract_1688.js 提取数据

# 2. 利润分析
python src/manual_picker.py

# 3. 查看推荐商品
cat data/recommended_products.json
```

## 📁 项目结构

```
ecommerce-agent/
├── frontend/           # 前端页面
│   └── index.html     # Web 控制台
├── backend/            # 后端 API 服务
│   └── main.py        # FastAPI 应用
├── src/                # 核心业务逻辑
│   ├── alibaba_scraper.py    # 1688 采集
│   ├── profit_analyzer.py    # 利润分析
│   ├── manual_picker.py      # 人工辅助工具
│   ├── media_downloader.py   # 图片下载
│   └── tiktok_uploader.py    # TikTok 上架
├── scripts/            # 辅助脚本
│   └── extract_1688.js # 1688 数据提取
├── config/             # 配置文件
├── data/               # 数据文件
├── output/             # 输出文件
└── logs/               # 日志文件
```

## 🌐 Web API

### 端点列表

| 端点 | 方法 | 功能 |
|------|------|------|
| `/` | GET | Web 控制台 |
| `/api/status` | GET | 系统状态 |
| `/api/stats` | GET | 统计数据 |
| `/api/products` | GET | 商品列表 |
| `/api/recommendations` | GET | 推荐商品 |
| `/api/analyze` | POST | 开始分析 |
| `/api/tasks/{id}` | GET | 任务状态 |
| `/api/logs` | GET | 系统日志 |
| `/docs` | GET | API 文档（Swagger） |

### 使用示例

```bash
# 获取系统状态
curl http://localhost:8000/api/status

# 获取统计数据
curl http://localhost:8000/api/stats

# 开始利润分析
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"min_profit_margin": 0.3}'

# 查看 API 文档
# 浏览器访问：http://localhost:8000/docs
```

## 📥 商品导入流程

### 从 1688 导入商品

1. **访问 1688.com** 搜索目标商品
   - 推荐关键词：跨境专供、TikTok 同款、一件代发

2. **打开开发者工具**
   - 按 `F12` 或右键 → 检查
   - 切换到 `Console` 标签

3. **运行提取脚本**
   ```javascript
   // 复制 scripts/extract_1688.js 内容并粘贴运行
   ```

4. **保存数据**
   - 复制输出的 JSON
   - 保存为 `data/1688_products.json`

5. **执行分析**
   - Web 控制台点击"开始分析"
   - 或运行 `python src/manual_picker.py`

## ⚙️ 配置

### 修改服务端口

编辑 `backend/main.py`:

```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,  # 修改端口
    log_level="info"
)
```

### 修改利润率阈值

在 Web 控制台或 API 请求中设置：

```json
{
  "min_profit_margin": 0.4  // 40% 最低利润率
}
```

## 🛡️ 生产部署

### 使用 systemd 服务

```bash
# 创建服务文件
sudo nano /etc/systemd/system/ecommerce-agent.service

# 启动服务
sudo systemctl enable ecommerce-agent
sudo systemctl start ecommerce-agent
```

详见 `WEB_GUIDE.md`

## 📋 技术栈

- **后端**: FastAPI + Uvicorn
- **前端**: 原生 HTML/CSS/JavaScript
- **数据处理**: Python + pandas
- **图片处理**: Pillow
- **配置管理**: YAML

## 📖 文档

- `README.md` - 项目说明（本文件）
- `QUICKSTART.md` - 快速开始指南
- `WEB_GUIDE.md` - Web 控制台使用指南
- `CURRENT_STATUS.md` - 当前开发状态
- `PROJECT_SUMMARY.md` - 项目总结

## ⚠️ 注意事项

**合规提醒:**
- 遵守各平台 robots.txt 和使用条款
- 注意图片版权
- TikTok 上架需符合平台规范

**反爬虫:**
- 使用浏览器自动化而非直接请求
- 设置合理的请求间隔
- 可能需要代理 IP

---

**开发完成** ✅ | **Web 控制台** ✅ | **API 服务** ✅
