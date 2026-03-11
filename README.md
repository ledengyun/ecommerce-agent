# 🛒 电商选品上架 Agent

自动化的电商选品与 TikTok 上架系统

## 功能流程

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. 1688 选品    │ ──→ │  2. 利润分析    │ ──→ │  3. 素材下载    │ ──→ │  4. TikTok 上架  │
│  热销/爆款采集   │     │  供货价→零售价   │     │  商品轮播图      │     │  自动发布       │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 模块说明

### 1. 1688 选品采集 (`src/alibaba_scraper.py`)
- 目标平台：1688（移动端）
- 采集内容：商品标题、供货价、销量、图片 URL、商品链接
- 选品关键词：跨境专供、TikTok 同款、一件代发等
- 输出：`data/1688_products.json`

### 2. 利润分析 (`src/supplier_finder.py`)
- 功能：计算利润率、建议零售价
- 输出：`data/supplier_matches.json`（含利润分析）

### 3. 素材获取 (`src/media_downloader.py`)
- 下载商品主图、轮播图
- 可选：图片去水印、尺寸调整
- 输出：`output/product_images/{product_id}/`

### 4. TikTok 上架 (`src/tiktok_uploader.py`)
- 自动填写商品信息
- 上传图片素材
- 设置价格、库存、标签
- 发布商品

## 技术栈

- **浏览器自动化**: OpenClaw browser 工具 / Playwright
- **数据处理**: Python + pandas
- **图片处理**: Pillow / OpenCV
- **配置管理**: YAML

## 快速开始

```bash
# 1. 配置平台账号（config/credentials.yaml）
# 2. 运行采集流程
python src/product_scraper.py
# 3. 查找供应商
python src/supplier_finder.py
# 4. 下载素材
python src/media_downloader.py
# 5. 上架 TikTok
python src/tiktok_uploader.py
```

## 注意事项

⚠️ **合规提醒**:
- 遵守各平台 robots.txt 和使用条款
- 注意图片版权
- TikTok 上架需符合平台规范

⚠️ **反爬虫**:
- 使用浏览器自动化而非直接请求
- 设置合理的请求间隔
- 可能需要代理 IP

## 配置

编辑 `config/settings.yaml` 设置：
- 采集数量（默认 10 个商品）
- 利润阈值
- TikTok 店铺信息
- 图片处理参数
