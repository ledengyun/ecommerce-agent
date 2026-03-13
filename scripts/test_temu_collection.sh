#!/bin/bash
# Temu 数据采集测试脚本

echo "============================================================"
echo "  Temu 数据采集测试"
echo "============================================================"
echo ""

cd "$(dirname "$0")/.."

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import bs4" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  未安装 BeautifulSoup4，正在安装..."
    pip install beautifulsoup4 -q
fi

python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  未安装 requests，正在安装..."
    pip install requests -q
fi

echo "✅ 依赖检查完成"
echo ""

# 检查 ScraperAPI 密钥
if [ -n "$SCRAPERAPI_API_KEY" ]; then
    echo "✅ 检测到 ScraperAPI 密钥：${SCRAPERAPI_API_KEY:0:10}..."
    echo ""
    read -p "是否使用现有密钥测试？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入新的 ScraperAPI 密钥： " NEW_KEY
        export SCRAPERAPI_API_KEY="$NEW_KEY"
    fi
else
    echo "⚠️  未配置 ScraperAPI 密钥"
    echo ""
    echo "📝 请注册获取免费密钥："
    echo "   https://www.scraperapi.com"
    echo ""
    read -p "请输入您的 ScraperAPI 密钥： " API_KEY
    
    if [ -z "$API_KEY" ]; then
        echo "❌ 密钥不能为空"
        exit 1
    fi
    
    export SCRAPERAPI_API_KEY="$API_KEY"
    
    # 询问是否保存
    echo ""
    read -p "是否保存到 ~/.bashrc？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "export SCRAPERAPI_API_KEY=\"$API_KEY\"" >> ~/.bashrc
        echo "✅ 已保存到 ~/.bashrc"
    fi
fi

echo ""
echo "============================================================"
echo "  开始测试采集"
echo "============================================================"
echo ""

# 运行测试
python3 src/temu_scraper_direct.py

echo ""
echo "============================================================"
echo "  测试完成"
echo "============================================================"
echo ""

# 检查是否生成了数据文件
LATEST_FILE=$(ls -t data/temu_products_*.json 2>/dev/null | head -1)

if [ -n "$LATEST_FILE" ]; then
    echo "✅ 数据文件已生成：$LATEST_FILE"
    echo ""
    
    # 统计商品数量
    COUNT=$(python3 -c "import json; print(len(json.load(open('$LATEST_FILE'))))")
    echo "📦 商品数量：$COUNT"
    
    echo ""
    read -p "是否导入数据库？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "📊 正在导入数据库..."
        python3 database/auto_import.py --mode once --file "$LATEST_FILE"
    fi
else
    echo "⚠️  未生成数据文件"
    echo ""
    echo "可能的原因："
    echo "1. API 密钥无效"
    echo "2. 网络问题"
    echo "3. Temu 页面结构变化"
    echo ""
    echo "建议："
    echo "1. 检查 ScraperAPI 余额：https://app.scraperapi.com/dashboard"
    echo "2. 查看详细日志"
fi

echo ""
echo "============================================================"
echo "  下一步"
echo "============================================================"
echo ""
echo "1. 查看完整文档："
echo "   cat docs/TEMU_DATA_COLLECTION_STRATEGY.md"
echo ""
echo "2. 启动自动导入服务："
echo "   python3 database/auto_import.py --mode watch"
echo ""
echo "3. 多平台采集："
echo "   python3 -c \"from src.data_collector import DataCollector; c = DataCollector(); c.collect('home goods', ['1688', 'temu'], 20)\""
echo ""
