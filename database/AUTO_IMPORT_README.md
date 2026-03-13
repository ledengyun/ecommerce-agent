# 自动数据导入功能

让第三方采集的数据自动写入 `products` 表，无需手动运行导入脚本。

## 🎯 功能概述

支持三种数据导入方式：

1. **目录监听模式** - 自动监控 `data/incoming/` 目录，新文件自动导入
2. **HTTP API 模式** - 接收浏览器脚本直接上传的数据
3. **单次导入模式** - 命令行手动导入指定文件

## 🚀 快速开始

### 方式一：目录监听（推荐）

适合浏览器脚本下载 JSON 后自动处理的场景。

```bash
# 1. 创建监听目录
mkdir -p /home/admin/.openclaw/workspace/ecommerce-agent/data/incoming

# 2. 启动监听服务
cd /home/admin/.openclaw/workspace/ecommerce-agent
python3 database/auto_import.py --mode watch
```

**使用方法：**
- 将采集的 JSON 文件放入 `data/incoming/` 目录
- 服务会自动处理并移动到 `data/processed/` 目录
- 数据写入数据库 `products` 表

### 方式二：HTTP API

适合浏览器脚本直接上传数据的场景。

```bash
# 启动 HTTP 服务
python3 database/auto_import.py --mode http --port 8080
```

**浏览器脚本上传示例：**

```javascript
fetch('http://localhost:8080', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        platform: '1688',
        products: [...]  // 商品数组
    })
});
```

### 方式三：单次导入

```bash
# 导入指定文件
python3 database/auto_import.py --mode once --file data/1688_products.json

# 导入前清空表
python3 database/auto_import.py --mode once --file data/1688_products.json --truncate
```

## 🔧 配置选项

编辑 `auto_import.py` 中的 `CONFIG` 字典：

```python
CONFIG = {
    'watch_dir': 'data/incoming',           # 监听目录
    'processed_dir': 'data/processed',      # 已处理目录
    'poll_interval': 5,                     # 轮询间隔（秒）
    'min_profit_margin': 0.3,               # 最低利润率阈值
    'retail_price_multiplier': 3.5,         # 零售价倍率
    'shipping_cost': 5.0,                   # 运费估算
}
```

或通过环境变量配置数据库：

```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=ecommerce_agent
```

## 📋 支持的 JSON 格式

### 格式一：带元数据的对象

```json
{
  "platform": "1688",
  "extracted_at": "2026-03-13T08:00:00Z",
  "products": [
    {
      "title": "商品标题",
      "price": "¥12.78",
      "image": "https://...",
      "url": "https://...",
      "sales": "已售 300+ 件"
    }
  ]
}
```

### 格式二：纯数组

```json
[
  {
    "title": "商品标题",
    "supplier_price": "12.78",
    "image_url": "https://...",
    "source_url": "https://..."
  }
]
```

### 字段映射（自动兼容）

| 标准字段 | 兼容字段 |
|---------|---------|
| title | name, product_title |
| price | supplier_price, sale_price, current_price |
| image_url | image, main_image, thumbnail |
| source_url | url, product_url, link |
| sales | sold_count |
| rating | score |

## 🔔 系统服务（可选）

将自动导入配置为系统服务，开机自启：

```bash
# 复制服务文件
sudo cp database/auto_import.service /etc/systemd/system/

# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start ecommerce-auto-import

# 开机自启
sudo systemctl enable ecommerce-auto-import

# 查看状态
sudo systemctl status ecommerce-auto-import

# 查看日志
sudo journalctl -u ecommerce-auto-import -f
```

## 📊 API 响应示例

**成功响应：**
```json
{
  "success": true,
  "imported": 45,
  "skipped": 0,
  "errors": 0,
  "total_in_db": 150,
  "recommended": 23,
  "platform": "1688",
  "timestamp": "2026-03-13T08:30:00"
}
```

**失败响应：**
```json
{
  "success": false,
  "message": "数据库连接失败"
}
```

## 🛠️ 故障排查

### 问题：文件没有被自动处理

**检查：**
1. 确认文件在 `data/incoming/` 目录
2. 确认监听服务正在运行
3. 查看日志是否有错误

```bash
# 检查服务状态
ps aux | grep auto_import

# 查看日志
tail -f /var/log/syslog | grep ecommerce-auto-import
```

### 问题：HTTP 上传失败

**检查：**
1. 确认 HTTP 服务正在运行
2. 确认端口没有被占用
3. 检查 CORS（如果是跨域请求）

```bash
# 测试服务
curl http://localhost:8080

# 检查端口
netstat -tlnp | grep 8080
```

### 问题：数据导入后利润率为空

**原因：** 价格解析失败

**解决：** 检查 JSON 中价格字段格式，确保包含数字：
- ✅ `"price": "¥12.78"` 
- ✅ `"price": "12.78"`
- ❌ `"price": "面议"`

## 📝 使用示例

### 完整工作流

```bash
# 1. 启动 HTTP 服务（终端 1）
cd /home/admin/.openclaw/workspace/ecommerce-agent
python3 database/auto_import.py --mode http --port 8080

# 2. 在浏览器运行采集脚本（终端 2）
# 打开 1688 搜索页 → F12 → Console → 粘贴 extract_1688_auto_v2.js

# 3. 查看数据库（终端 3）
mysql -u root -p
USE ecommerce_agent;
SELECT title, supplier_price, profit_margin, recommend FROM products ORDER BY created_at DESC LIMIT 10;
```

## 🔐 安全提示

- HTTP 服务默认监听所有接口（0.0.0.0），生产环境建议限制 IP
- 数据库密码建议通过环境变量配置，不要硬编码
- 考虑添加 API 认证（如 token 验证）
