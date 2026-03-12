#!/bin/bash
# 电商选品 Agent - Web 服务启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 电商选品 Agent - Web 服务"
echo "================================"

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 创建必要目录
mkdir -p data output logs

# 启动服务
echo ""
echo "✅ 准备就绪！"
echo ""
echo "📍 访问地址："
echo "   - 前端页面：http://localhost:8000"
echo "   - API 文档：http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 backend/main.py
