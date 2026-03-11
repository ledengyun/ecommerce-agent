# 🚀 电商 Agent 开发指南

## 项目现状

✅ **已完成：**
- 项目结构搭建
- 配置文件模板
- 4 个核心模块代码框架
- 日志系统配置

⚠️ **待实现：**
- 各平台的浏览器自动化逻辑（核心！）
- TikTok Shop API 或自动化操作
- 图片下载与处理
- 错误处理与重试机制

---

## 下一步工作

### 1️⃣ 实现 Amazon/Temu 商品采集

需要实现 `src/product_scraper.py` 中的浏览器自动化：

```python
# 使用 OpenClaw browser 工具
# 示例：访问 Amazon Best Sellers
browser(action="open", url="https://www.amazon.com/best-sellers")
browser(action="snapshot")  # 获取页面结构
# 提取商品信息...
```

**关键点：**
- Amazon 有反爬虫，需要用 browser 工具模拟真人操作
- Temu 相对友好，但也需要浏览器自动化
- 提取字段：标题、价格、评分、销量、图片 URL

### 2️⃣ 实现 1688/义乌购供应商搜索

需要实现 `src/supplier_finder.py`：

```python
# 1688 搜索
browser(action="open", url="https://s.1688.com/selloffer/offer_search.htm?keywords=xxx")
# 以图搜图功能（更准确）
```

**关键点：**
- 1688 需要登录才能看完整信息
- 以图搜图比关键词搜索更准确
- 需要提取：供货价、MOQ、运费、商家评分

### 3️⃣ 实现图片下载

`src/media_downloader.py` 可以用：
- `requests` 直接下载（简单）
- OpenClaw `browser` 工具截图（绕过反爬）

### 4️⃣ 实现 TikTok 上架

**两种方式：**

**A. 浏览器自动化（推荐起步）**
```python
# 访问 TikTok Shop 后台
browser(action="open", url="https://www.tiktok.com/seller")
# 点击"添加商品"
browser(action="click", ref="add_product_button")
# 填写表单...
```

**B. TikTok API（需要申请）**
- TikTok Shop 有官方 API
- 需要商家资质审核

---

## 技术要点

### OpenClaw Browser 工具使用

```python
# 在你的 Python 代码中调用 OpenClaw 工具
# 方式 1：通过 subprocess 调用 openclaw CLI
import subprocess
result = subprocess.run(
    ['openclaw', 'browser', 'open', '--url', 'https://example.com'],
    capture_output=True, text=True
)

# 方式 2：在 OpenClaw 会话中直接使用 browser 工具（推荐）
# 让 AI agent 直接调用 browser 工具完成自动化
```

### 浏览器自动化流程

```
1. open → 打开目标页面
2. snapshot → 获取页面结构（带 refs）
3. click/type → 操作页面元素
4. screenshot → 必要时截图
5. evaluate → 执行 JS 提取数据
```

---

## 测试建议

1. **先手动测试流程**
   - 手动访问各平台，熟悉页面结构
   - 记录需要操作的元素（按钮、表单）

2. **从小规模开始**
   - 先采集 1-2 个商品测试
   - 验证整个流程后再批量运行

3. **注意合规**
   - 遵守各平台 robots.txt
   - 设置合理的请求间隔
   - 不要高频请求

---

## 项目结构

```
ecommerce-agent/
├── README.md              # 项目说明
├── main.py                # 主入口
├── requirements.txt       # Python 依赖
├── config/
│   ├── settings.yaml      # 配置文件
│   └── credentials.yaml.example  # 账号配置模板
├── src/
│   ├── product_scraper.py   # Step 1: 商品采集
│   ├── supplier_finder.py   # Step 2: 供应商查找
│   ├── media_downloader.py  # Step 3: 图片下载
│   └── tiktok_uploader.py   # Step 4: TikTok 上架
├── data/                    # 中间数据
│   ├── hot_products.json
│   └── supplier_matches.json
├── output/                  # 输出结果
│   ├── product_images/
│   └── tiktok_upload_log.json
└── logs/                    # 日志
```

---

## 需要我帮你实现哪个模块？

我可以帮你：
1. 🕷️ 编写具体的浏览器自动化代码
2. 📸 实现图片下载与处理
3. 📤 对接 TikTok Shop（需要你的账号信息）
4. 🧪 搭建测试环境

**告诉我你想先从哪个平台开始！**
