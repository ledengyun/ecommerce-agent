# 电商选品 Agent - 更新日志

## 2026-03-11 - 转向 1688 方案

### 变更原因
- Temu 访问需要特殊网络环境
- 1688 是货源平台，更直接
- 利润计算更简单（供货价→零售价）

### 已完成
- ✅ 创建 `src/1688_scraper.py`（增强版）
- ✅ 支持移动端页面（反爬较松）
- ✅ JavaScript 直接提取数据
- ✅ 多关键词批量搜索
- ✅ 自动去重

### 1688 反爬应对策略

**问题：** 1688 检测到自动化访问会显示验证码

**解决方案：**

1. **使用移动端页面** (`m.1688.com`)
   - 反爬机制较宽松
   - 页面结构简单，更容易提取

2. **JavaScript 直接提取**
   - 不依赖 HTML 结构解析
   - 直接在浏览器上下文执行 JS

3. **合理延迟**
   - 每次请求间隔 2-5 秒
   - 模拟真人操作

4. **关键词搜索代替浏览榜单**
   - 榜单页面反爬严
   - 搜索页面相对宽松

### 推荐关键词

```python
keywords = [
    '跨境专供',      # 专为跨境电商供货
    '亚马逊爆款',    # Amazon 热销同款
    'TikTok 同款',   # TikTok 热门商品
    '抖音网红',      # 抖音带货商品
    '一件代发',      # 支持 dropshipping
    '家居好物',      # 家居类目
    '创意小商品',    # 低价引流款
]
```

### 下一步

1. **测试采集脚本**
   ```bash
   cd ecommerce-agent
   python src/1688_scraper.py
   ```

2. **调整选择器**
   - 根据实际页面结构调整 JS 选择器
   - 在 `extract_products_manual()` 中修改

3. **完善利润计算**
   - 1688 价格通常是区间价（如 ¥10.50-15.80）
   - 需要解析最低价作为成本
   - 加上运费、平台佣金计算最终利润

4. **对接 TikTok**
   - 实现自动上架
   - 需要 TikTok Shop 账号

---

## 项目结构（更新）

```
ecommerce-agent/
├── README.md
├── IMPLEMENTATION_GUIDE.md
├── DEV_LOG.md              # 开发记录（本文件）
├── main.py
├── requirements.txt
├── config/
│   ├── settings.yaml
│   └── credentials.yaml.example
└── src/
    ├── 1688_scraper.py     # ⭐ 1688 采集（新增）
    ├── temu_scraper.py     # Temu 采集（备选）
    ├── product_scraper.py  # 通用采集接口
    ├── supplier_finder.py  # 供应商比价
    ├── media_downloader.py # 图片下载
    └── tiktok_uploader.py  # TikTok 上架
```

---

## 测试计划

### Phase 1: 采集测试
- [ ] 测试 1688 移动端页面访问
- [ ] 验证 JavaScript 提取逻辑
- [ ] 采集 10 个商品验证数据质量

### Phase 2: 利润计算
- [ ] 解析 1688 价格区间
- [ ] 添加运费估算
- [ ] 计算 TikTok 售价建议

### Phase 3: 图片处理
- [ ] 下载商品主图
- [ ] 图片去水印（可选）
- [ ] 尺寸标准化

### Phase 4: TikTok 上架
- [ ] 登录 TikTok Shop
- [ ] 自动填写商品信息
- [ ] 批量上架测试

---

## 注意事项

⚠️ **合规提醒：**
- 1688 数据仅供选品参考
- 商品图片注意版权
- TikTok 上架需符合平台规范

⚠️ **技术限制：**
- 1688 反爬可能变化，需要维护选择器
- 大量采集可能需要代理 IP
- TikTok 上架 API 需要商家资质
