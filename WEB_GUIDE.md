# 🌐 Web 控制台使用指南

## 项目架构

```
ecommerce-agent/
├── frontend/          # 前端页面
│   └── index.html    # 单页应用
├── backend/           # 后端 API
│   └── main.py       # FastAPI 服务
├── src/              # 核心业务逻辑
├── data/             # 数据文件
├── output/           # 输出文件
└── logs/             # 日志文件
```

## 🚀 快速启动

### 方式 1：使用启动脚本（推荐）

```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent
chmod +x start.sh
./start.sh
```

### 方式 2：手动启动

```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 启动后端服务
cd /home/admin/.openclaw/workspace/ecommerce-agent
python3 backend/main.py
```

## 📍 访问地址

启动后访问：

- **前端控制台**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **API 状态**: http://localhost:8000/api/status

## ✨ 功能特性

### 前端控制台

- 📊 **实时统计** - 商品总数、推荐数、平均利润率
- 📦 **商品列表** - 查看所有商品和推荐商品
- 🎯 **一键分析** - 点击按钮执行利润分析
- 📋 **实时日志** - 查看系统运行日志

### 后端 API

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/status` | GET | 系统状态 |
| `/api/stats` | GET | 统计数据 |
| `/api/products` | GET | 商品列表 |
| `/api/recommendations` | GET | 推荐商品 |
| `/api/analyze` | POST | 开始分析 |
| `/api/tasks/{id}` | GET | 任务状态 |
| `/api/logs` | GET | 系统日志 |

## 📥 使用流程

### 1. 导入商品数据

```bash
# 访问 1688.com 搜索商品
# 按 F12 打开开发者工具 → Console
# 运行 scripts/extract_1688.js
# 复制 JSON 保存为 data/1688_products.json
```

### 2. 打开 Web 控制台

浏览器访问 http://localhost:8000

### 3. 执行利润分析

点击"开始分析"按钮，等待分析完成

### 4. 查看推荐商品

切换到"推荐"标签，查看高利润商品

## 🔧 配置选项

### 修改服务端口

编辑 `backend/main.py`:

```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,  # 修改这里
    log_level="info"
)
```

### 修改利润率阈值

前端默认使用 30% 最低利润率，可在 `frontend/index.html` 中修改：

```javascript
body: JSON.stringify({ min_profit_margin: 0.3 })  // 改为 0.4 即 40%
```

## 🛡️ 生产环境部署

### 使用 systemd 服务

创建 `/etc/systemd/system/ecommerce-agent.service`:

```ini
[Unit]
Description=Ecommerce Agent Web Service
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/.openclaw/workspace/ecommerce-agent
ExecStart=/usr/bin/python3 backend/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable ecommerce-agent
sudo systemctl start ecommerce-agent
sudo systemctl status ecommerce-agent
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📝 注意事项

1. **首次启动** - 确保已安装所有依赖
2. **数据目录** - 确保 `data/`, `output/`, `logs/` 目录存在且可写
3. **端口占用** - 如果 8000 端口被占用，修改配置中的端口号
4. **防火墙** - 如需远程访问，开放对应端口

## 🐛 故障排查

### 服务无法启动

```bash
# 检查端口占用
lsof -i :8000

# 检查依赖
pip3 list | grep -i fastapi

# 查看日志
tail -f logs/ecommerce_agent.log
```

### 前端页面空白

- 检查浏览器控制台是否有错误
- 确认后端服务正在运行
- 清除浏览器缓存后重试

### API 请求失败

- 检查网络连接
- 确认服务地址和端口正确
- 查看后端日志定位问题

---

**技术支持**: 查看项目文档或提交 Issue
