#!/bin/bash
# 1688 商品数据导入脚本
# 自动查找下载的文件并导入数据库

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."
DATA_DIR="$PROJECT_ROOT/data"

echo "======================================"
echo "📦 1688 商品数据导入工具"
echo "======================================"
echo ""

# 确保数据目录存在
mkdir -p "$DATA_DIR"

# 查找最近下载的 1688 文件
echo "🔍 查找最近下载的 1688 商品文件..."
DOWNLOAD_FILE=$(ls -t /home/admin/.openclaw/workspace/Download/1688_products_*.json 2>/dev/null | head -1)

if [ -z "$DOWNLOAD_FILE" ]; then
    echo "❌ 未找到下载的文件：~/Downloads/1688_products_*.json"
    echo ""
    echo "请确认："
    echo "1. 已在浏览器中运行 extract_1688_auto.js 脚本"
    echo "2. 文件已下载到 ~/Downloads/ 目录"
    echo ""
    echo "或者手动指定文件："
    echo "  ./import_downloaded.sh /path/to/your/file.json"
    exit 1
fi

echo "✅ 找到文件：$DOWNLOAD_FILE"
echo ""

# 复制到项目目录
TARGET_FILE="$DATA_DIR/1688_products.json"
echo "📋 复制文件到：$TARGET_FILE"
cp "$DOWNLOAD_FILE" "$TARGET_FILE"
echo "✅ 复制完成"
echo ""

# 显示文件信息
echo "📊 文件信息:"
ls -lh "$TARGET_FILE"
echo ""

# 显示商品数量
echo "📦 商品统计:"
TOTAL=$(python3 -c "import json; data=json.load(open('$TARGET_FILE')); print(len(data.get('products', [])))")
echo "   总商品数：$TOTAL"
echo ""

# 询问是否导入数据库
read -p "是否导入到 MySQL 数据库？(y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗄️  导入数据库..."
    cd "$PROJECT_ROOT"
    python3 database/import_data.py
    
    echo ""
    echo "======================================"
    echo "✅ 导入完成！"
    echo "======================================"
    echo ""
    echo "🌐 访问 Web 控制台："
    echo "   http://localhost:8000"
    echo ""
    echo "💡 提示：在控制台点击"开始分析"查看利润分析结果"
    echo ""
else
    echo ""
    echo "======================================"
    echo "✅ 文件已保存到：$TARGET_FILE"
    echo "======================================"
    echo ""
    echo "稍后可以手动运行："
    echo "  python3 database/import_data.py"
    echo ""
fi
