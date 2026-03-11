# 🚀 快速开始指南

## 1 分钟上手

### 前置条件

- Python 3.8+
- OpenClaw 环境（需要 browser 工具）
- 能访问 1688.com 的网络环境

### 安装依赖

```bash
cd ecommerce-agent
pip install -r requirements.txt
```

### 测试采集

```bash
# 运行测试脚本
python test_1688.py

# 或直接采集
python src/alibaba_scraper.py
```

### 完整流程

```bash
# Step 1: 采集 1688 商品
python src/alibaba_scraper.py

# Step 2: 利润分析（待实现）
python src/supplier_finder.py

# Step 3: 下载图片（待实现）
python src/media_downloader.py

# Step 4: TikTok 上架（待实现）
python src/tiktok_uploader.py
```

---

## 项目结构

```
ecommerce-agent/
├── README.md              # 项目说明
├── QUICKSTART.md          # 本文件
├── DEV_LOG.md             # 开发记录
├── main.py                # 主入口
├── test_1688.py           # 测试脚本
├── requirements.txt       # Python 依赖
├── config/
│   └── settings.yaml      # 配置文件
└── src/
    ├── alibaba_scraper.py   # ⭐ 1688 采集
    ├── supplier_finder.py   # 利润分析
    ├── media_downloader.py  # 图片下载
    └── tiktok_uploader.py   # TikTok 上架
```

---

## 配置说明

编辑 `config/settings.yaml`：

```yaml
scraper:
  products_limit: 10        # 采集数量
  keywords:                  # 选品关键词
    - 跨境专供
    - TikTok 同款
    - 一件代发
```

---

## 常见问题

### Q: 采集不到商品？

**A:** 可能是 1688 页面结构变化，需要调整选择器：

1. 打开 `src/alibaba_scraper.py`
2. 找到 `extract_products_manual()` 函数
3. 调整 JS 中的选择器：
   ```javascript
   const selectors = [
       '.offer-item',      // 尝试其他选择器
       '.product-item',
       '.m-offer-item'
   ];
   ```

### Q: 显示验证码/反爬？

**A:** 
- 使用移动端页面（默认已启用）
- 增加请求延迟（`wait(5)` 改为更长时间）
- 减少采集数量

### Q: 如何自定义选品关键词？

**A:** 修改 `config/settings.yaml` 中的 `keywords` 列表，或在代码中传入：

```python
scrape_1688_products(
    keywords=['你的关键词'],
    limit=10
)
```

---

## 下一步

1. **测试采集功能** - 运行 `python test_1688.py`
2. **调整选择器** - 根据实际页面结构优化
3. **完善利润计算** - 实现供货价→零售价转换
4. **对接 TikTok** - 实现自动上架

---

## 需要帮助？

查看详细文档：
- `README.md` - 项目说明
- `IMPLEMENTATION_GUIDE.md` - 开发指南
- `DEV_LOG.md` - 开发记录

有问题随时问我！🤖
