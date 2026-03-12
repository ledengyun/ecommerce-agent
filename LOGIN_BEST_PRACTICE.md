# 🔐 1688 登录采集 - 最佳实践方案

## ⚠️ 当前问题

通过自动化脚本登录 1688 会遇到以下问题：

1. **滑块验证** - 1688 登录时需要滑块验证，自动化难以处理
2. **Tab 丢失** - OpenClaw browser 的 tab 在页面跳转时可能丢失
3. **会话保持** - 登录状态难以在多次采集中保持

---

## ✅ 推荐方案：使用已登录的浏览器

### 方案说明

1. **手动登录一次** - 在浏览器中手动登录 1688 账号
2. **保存 Cookie/Session** - 浏览器会保存登录状态
3. **自动化采集** - 使用已登录的浏览器进行采集

### 实现方式

#### 方式 1：使用浏览器扩展/配置文件

如果使用 Chrome/Edge：

1. **找到浏览器用户数据目录**
   ```bash
   # Linux
   ~/.config/google-chrome/
   
   # macOS
   ~/Library/Application Support/Google/Chrome/
   
   # Windows
   C:\Users\你的用户名\AppData\Local\Google\Chrome\User Data\
   ```

2. **使用已有用户数据启动浏览器**
   ```bash
   openclaw browser open https://m.1688.com \
     --user-data-dir=/path/to/chrome/user/data
   ```

3. **在这个浏览器中登录 1688**
   - 打开后登录一次
   - 关闭浏览器
   - 下次启动会自动保持登录状态

#### 方式 2：导出 Cookie（推荐）

1. **在浏览器中登录 1688**
   - 使用 Chrome/Edge 打开 https://m.1688.com
   - 登录你的账号

2. **导出 Cookie**
   - 按 F12 打开开发者工具
   - 右键点击页面 → Network → 刷新页面
   - 右键任意请求 → Copy → Copy as cURL
   - 或使用扩展：EditThisCookie、Cookie Editor

3. **保存 Cookie 到文件**
   ```json
   // config/1688_cookies.json
   {
     "cookie": "_m_hk_token=xxx; _m_hk=xxx; ..."
   }
   ```

4. **采集时使用 Cookie**
   ```python
   # 在请求头中添加 Cookie
   headers = {
       'Cookie': config['cookie']
   }
   ```

---

## 🎯 当前最佳方案：人工辅助 + 自动化分析

由于登录自动化的复杂性，**推荐使用以下组合方案**：

### 流程

```
1. 人工访问 1688（已登录状态）
   ↓
2. 搜索目标商品
   ↓
3. 运行 JS 脚本提取数据
   ↓
4. 自动保存到 data/1688_products.json
   ↓
5. Web 控制台自动读取并进行利润分析
```

### 优势

- ✅ **无需处理登录** - 人工登录最可靠
- ✅ **绕过反爬** - 人工操作不会被检测
- ✅ **准确筛选** - 人工判断更精准
- ✅ **自动化分析** - 利润分析完全自动化

---

## 📝 人工辅助操作流程

### Step 1: 登录并搜索

1. 打开浏览器（Chrome/Edge）
2. 访问 https://m.1688.com
3. 登录你的 1688 账号
4. 搜索关键词（如"跨境专供"）

### Step 2: 提取数据

1. 按 F12 打开开发者工具
2. 切换到 Console 标签
3. 复制并运行 `scripts/extract_1688.js`
4. 复制输出的 JSON

### Step 3: 保存数据

1. 保存为 `data/1688_products.json`
2. 或直接在 Web 控制台粘贴

### Step 4: 自动分析

1. 访问 Web 控制台 http://localhost:8000
2. 点击"开始分析"
3. 查看推荐商品

---

## 🔧 如果一定要自动化登录

### 使用 Playwright（更强大的浏览器自动化）

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 启动浏览器（使用持久化上下文）
    browser = p.chromium.launch_persistent_context(
        user_data_dir="./browser_profile",
        headless=False
    )
    
    page = browser.new_page()
    page.goto("https://m.1688.com")
    
    # 手动登录一次后，下次会自动保持
    input("请在浏览器中登录 1688，然后按回车继续...")
    
    # 登录后进行搜索
    page.goto("https://m.1688.com/page/search.html?keywords=跨境专供")
    page.wait_for_timeout(5000)
    
    # 提取商品
    products = page.evaluate("""
        () => {
            const items = document.querySelectorAll('.offer-item');
            return Array.from(items).map(item => ({
                title: item.querySelector('.title')?.textContent,
                price: item.querySelector('.price')?.textContent,
                // ...
            }));
        }
    """)
    
    browser.close()
```

### 安装 Playwright

```bash
pip3 install playwright
playwright install chromium
```

---

## 📊 方案对比

| 方案 | 难度 | 稳定性 | 推荐度 |
|------|------|--------|--------|
| 人工辅助 + 自动分析 | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 浏览器配置文件 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 导出 Cookie | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 自动化登录脚本 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Playwright 持久化 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 💡 结论

**推荐使用人工辅助模式**，原因：

1. **登录问题** - 1688 登录需要滑块验证，自动化困难
2. **稳定性** - 人工操作最稳定，不会被反爬
3. **效率** - 人工筛选 + 自动分析效率最高
4. **成本** - 无需复杂的技术方案

**人工辅助不是妥协，而是最优解！**

---

## 📁 相关文件

- `scripts/extract_1688.js` - 人工辅助提取脚本
- `LOGIN_GUIDE.md` - 登录指南
- `1688_SCRAPER_TEST.md` - 自动化测试报告

---

**下一步：**
使用人工辅助模式，登录 1688 后运行 JS 脚本提取数据，然后享受自动化的利润分析！
