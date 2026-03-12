# 🎉 1688 商品提取 - 完整使用指南

## 🚀 快速开始（3 步完成）

### Step 1: 在浏览器中运行提取脚本

```bash
# 1. 打开 1688 搜索页（如搜索"方巾"、"跨境专供"等）
# 2. 按 F12 打开开发者工具 → Console 标签
# 3. 输入：allow pasting → Enter
# 4. 复制并运行脚本：
cat /home/admin/.openclaw/workspace/ecommerce-agent/scripts/extract_1688_auto.js
# 5. 按 Enter 运行
```

**脚本会自动：**
- ✅ 提取商品信息（标题、价格、图片、链接）
- ✅ **自动下载 JSON 文件** 到 `~/Downloads/` 或 `~/workspace/Download/`
- ✅ 在 Console 输出 JSON（可备份）

---

### Step 2: 运行导入脚本

```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent
./scripts/import_downloaded.sh
```

**导入脚本会：**
- 🔍 自动查找最近下载的 1688 文件
- 📋 复制到 `data/1688_products.json`
- 🗄️ 导入 MySQL 数据库
- ✅ 显示统计信息

---

### Step 3: 访问 Web 控制台

```
http://localhost:8000
```

在控制台中：
- 📊 查看商品列表
- 🎯 点击"开始分析"
- 📈 查看利润分析结果

---

## 📊 当前数据状态

**已导入商品：** 10 个  
**推荐商品：** 9 个  
**平均利润率：** 11.13%

**商品示例：**
| 商品 | 供货价 | 利润率 | 推荐 |
|------|--------|--------|------|
| 时尚复古花朵图案印花褶皱 70 方巾 | ¥6.45 | 49.28% | ✅ |
| 春夏季新款清新时尚动漫图案方巾 | ¥4.73 | 41.23% | ✅ |
| ... | ... | ... | ... |

---

## 📁 相关文件

### 脚本文件

| 文件 | 功能 |
|------|------|
| `scripts/extract_1688_auto.js` | **自动保存版**（推荐使用） |
| `scripts/extract_1688.js` | 标准版（手动复制） |
| `scripts/extract_1688_debug.js` | 调试版（详细日志） |
| `scripts/import_downloaded.sh` | 自动导入脚本 |

### 数据文件

| 文件 | 说明 |
|------|------|
| `data/1688_products.json` | 商品数据文件 |
| `database/import_data.py` | 数据库导入脚本 |

### 文档

| 文件 | 说明 |
|------|------|
| `scripts/AUTO_SAVE_GUIDE.md` | 自动保存版详细说明 |
| `scripts/README.md` | 脚本使用说明 |
| `LOGIN_BEST_PRACTICE.md` | 登录最佳实践 |

---

## 💡 使用技巧

### 推荐搜索关键词

```
方巾
跨境专供
TikTok 同款
一件代发
抖音网红
亚马逊爆款
家居好物
美妆工具
手机配件
```

### 提高提取成功率

1. **使用桌面版页面** - www.1688.com（商品更多）
2. **登录后再搜索** - 可以看到完整价格
3. **向下滚动加载** - 加载更多商品后再提取
4. **选择具体类目** - 如"方巾"比"百货"更精准

### 价格解析优化

脚本会自动处理：
- ✅ `¥6.45` → 6.45
- ✅ `¥6.45 月卡价` → 6.45
- ✅ `¥6.45≥1 件` → 6.45
- ✅ `￥10.50-15.80` → 10.50

---

## 🐛 常见问题

### Q1: 没有自动下载文件？

**检查：**
1. 浏览器是否阻止了下载
2. Console 是否有错误信息

**解决：**
- 允许浏览器下载
- 检查 Console 输出
- 手动复制 JSON 保存

### Q2: 导入脚本找不到文件？

**解决：**
```bash
# 手动指定文件
./import_downloaded.sh ~/Downloads/1688_products_xxx.json

# 或手动复制
cp ~/Downloads/1688_products_xxx.json data/1688_products.json
python3 database/import_data.py
```

### Q3: 提取到的商品数量为 0？

**解决：**
1. 确认在搜索结果页（不是首页）
2. 向下滚动加载更多商品
3. 刷新页面后重试
4. 登录 1688 账号

### Q4: 利润率太低？

**原因：** 供货价过高或零售价倍率过低

**解决：**
```sql
-- 调整零售价倍率（当前 3.5 倍）
UPDATE settings SET setting_value = '4.0' 
WHERE setting_key = 'retail_price_multiplier';

-- 然后重新运行分析
```

---

## 📋 完整工作流程

```
┌─────────────────────────────────────────┐
│  1. 浏览器访问 1688 搜索商品              │
│     https://www.1688.com                │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  2. F12 → Console → 运行脚本            │
│     extract_1688_auto.js                │
│     （自动下载 JSON）                    │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  3. 运行导入脚本                         │
│     ./import_downloaded.sh              │
│     （自动查找 + 复制 + 导入）            │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  4. 数据已保存到                         │
│     - data/1688_products.json           │
│     - MySQL 数据库                       │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  5. 访问 Web 控制台                      │
│     http://localhost:8000               │
│     点击"开始分析"                       │
└─────────────────────────────────────────┘
```

---

## 🎯 下一步

### 继续采集更多商品

```bash
# 1. 在 1688 搜索新关键词
# 2. 运行 extract_1688_auto.js
# 3. 运行 ./import_downloaded.sh
# 4. 刷新 Web 控制台
```

### 优化选品策略

1. **调整利润率阈值**
   ```sql
   UPDATE settings SET setting_value = '0.4' 
   WHERE setting_key = 'min_profit_margin';
   ```

2. **修改零售价倍率**
   ```sql
   UPDATE settings SET setting_value = '4.0' 
   WHERE setting_key = 'retail_price_multiplier';
   ```

3. **重新分析**
   - 在 Web 控制台点击"开始分析"

---

## 📞 需要帮助？

查看日志：
```bash
tail -f logs/ecommerce_agent.log
```

检查数据库：
```bash
mysql -u root -p'EcommerceAgent2026!' -e "USE ecommerce_agent; SELECT COUNT(*) FROM products;"
```

查看统计：
```bash
curl http://localhost:8000/api/stats
```

---

**现在请继续采集更多商品吧！** 🚀

遇到问题随时告诉我。
