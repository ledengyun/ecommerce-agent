# 🔐 1688 登录采集使用指南

## 📋 前提条件

你需要提供一个 1688 买家账号（普通买家账号即可）

---

## ⚙️ 配置账号

### 方式 1：编辑配置文件（推荐）

编辑 `config/1688_credentials.json`：

```json
{
    "username": "13800138000",
    "password": "your_password"
}
```

### 方式 2：代码中直接传入

```python
from src.alibaba_scraper_login import scrape_1688_products

products = scrape_1688_products(
    keywords=["跨境专供", "TikTok 同款"],
    limit=15,
    username="13800138000",
    password="your_password"
)
```

---

## 🚀 使用方式

### 方式 1：运行测试脚本

```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent

# 先编辑 alibaba_scraper_login.py 填写账号密码
python3 src/alibaba_scraper_login.py
```

### 方式 2：在 Python 代码中调用

```python
from src.alibaba_scraper_login import Alibaba1688Scraper

# 创建采集器
scraper = Alibaba1688Scraper(
    use_mobile=True,
    username="13800138000",
    password="your_password"
)

# 执行采集
products = scraper.scrape(
    keywords=["跨境专供", "TikTok 同款"],
    max_products=15,
    do_login=True
)

# 关闭浏览器
scraper.close()

# 保存结果
scraper.save_products(products)
```

### 方式 3：使用便捷函数

```python
from src.alibaba_scraper_login import scrape_1688_products

products = scrape_1688_products(
    keywords=["跨境专供", "TikTok 同款", "一件代发"],
    limit=20,
    username="13800138000",
    password="your_password"
)

print(f"采集到 {len(products)} 个商品")
```

---

## 📊 登录采集流程

```
1. 打开 1688 登录页面
   ↓
2. 自动输入账号密码
   ↓
3. 点击登录按钮
   ↓
4. 等待登录验证（8-12 秒）
   ↓
5. 检查登录状态
   ↓
6. 登录成功后访问搜索页面
   ↓
7. 提取商品数据
   ↓
8. 保存为 JSON 文件
```

---

## 🎯 登录的优势

### 相比未登录状态：

| 项目 | 未登录 | 已登录 |
|------|--------|--------|
| 可访问页面 | 部分受限 | 全部可访问 |
| 商品价格 | 可能隐藏 | 完整显示 |
| 商品数量 | 较少 | 完整列表 |
| 反爬检测 | 较严格 | 较宽松 |
| 采集成功率 | 低 | 高 |

---

## 🔒 安全说明

### 账号安全

1. **使用买家账号** - 不需要卖家账号，普通买家账号即可
2. **本地存储** - 账号信息只保存在本地配置文件
3. **不上传云端** - 账号不会上传到任何服务器
4. **仅供采集** - 只用于浏览和采集商品数据

### 文件权限

建议设置配置文件权限：

```bash
chmod 600 config/1688_credentials.json
```

### 使用建议

- 使用不常用的小号
- 定期修改密码
- 不要频繁大量采集（避免被判定为异常）
- 每次采集间隔 5-10 分钟

---

## 🐛 常见问题

### Q1: 登录失败怎么办？

**检查：**
1. 账号密码是否正确
2. 是否需要短信验证
3. 网络是否正常

**解决：**
- 手动登录一次 1688，确保账号正常
- 如果需要短信验证，先在浏览器完成验证
- 检查网络连接

### Q2: 登录后还是采集不到商品？

**可能原因：**
1. 页面结构变化
2. 需要更长的等待时间
3. 选择器不匹配

**解决：**
```bash
# 运行调试脚本
python3 debug_1688.py
```

### Q3: 触发滑块验证怎么办？

**解决：**
1. 暂停采集，等待 15-30 分钟
2. 手动在浏览器完成滑块验证
3. 降低采集频率

### Q4: 账号被限制？

**解决：**
1. 停止采集 24 小时
2. 修改密码
3. 考虑使用其他账号

---

## 📁 输出文件

采集的商品保存在：

```
data/1688_products.json
```

格式示例：

```json
[
  {
    "index": 1,
    "title": "跨境专供网红创意家居用品",
    "price": "¥12.50-15.80",
    "sales": "1000+",
    "image": "https://...",
    "url": "https://detail.1688.com/offer/..."
  },
  ...
]
```

---

## 🎯 下一步

采集完成后：

1. **导入数据库**
   ```bash
   python3 database/import_data.py
   ```

2. **启动 Web 服务**
   ```bash
   python3 backend/main.py
   ```

3. **访问控制台**
   ```
   http://localhost:8000
   ```

4. **点击"开始分析"** - 自动进行利润分析

---

## 📞 需要帮助？

如果遇到问题：

1. 查看日志文件 `logs/ecommerce_agent.log`
2. 运行调试脚本 `python3 debug_1688.py`
3. 检查 1688_SCRAPER_TEST.md 了解已知问题

---

**账号信息（请填入）：**
- 用户名：_______________
- 密码：_______________

**填写后运行：**
```bash
python3 src/alibaba_scraper_login.py
```
