#!/bin/bash
# API 密钥配置脚本

echo "================================================"
echo "  Rainforest API 密钥配置"
echo "================================================"
echo ""

# 检查是否已有配置
if [ -n "$RAINFOREST_API_KEY" ]; then
    echo "✅ 检测到已配置的 API 密钥："
    echo "   ${RAINFOREST_API_KEY:0:10}..."
    echo ""
    read -p "是否要重新配置？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ 使用现有配置"
        exit 0
    fi
fi

# 输入新的 API 密钥
echo ""
echo "📝 请输入您的 Rainforest API 密钥："
echo "   (如果没有，请访问 https://www.rainforestapi.com 注册)"
echo ""
read -p "API Key: " API_KEY

if [ -z "$API_KEY" ]; then
    echo "❌ API 密钥不能为空"
    exit 1
fi

# 验证密钥格式（应该是字母数字组合）
if [[ ! "$API_KEY" =~ ^[a-zA-Z0-9]+$ ]]; then
    echo "⚠️  警告：API 密钥格式可能不正确"
    read -p "继续配置？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 保存到环境变量（临时）
export RAINFOREST_API_KEY="$API_KEY"

# 询问是否永久保存
echo ""
read -p "是否永久保存 API 密钥到 ~/.bashrc？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 备份 .bashrc
    cp ~/.bashrc ~/.bashrc.backup.$(date +%Y%m%d_%H%M%S)
    
    # 移除旧的配置（如果有）
    sed -i '/RAINFOREST_API_KEY/d' ~/.bashrc
    
    # 添加新配置
    echo "export RAINFOREST_API_KEY=\"$API_KEY\"" >> ~/.bashrc
    
    echo "✅ API 密钥已保存到 ~/.bashrc"
    echo "💡 运行 'source ~/.bashrc' 或重新打开终端生效"
else
    echo "✅ API 密钥已设置（仅当前终端会话有效）"
fi

# 测试 API 连接
echo ""
echo "🧪 测试 API 连接..."
cd "$(dirname "$0")/.."

python3 -c "
import os
import requests

api_key = os.getenv('RAINFOREST_API_KEY')
if not api_key:
    print('❌ 未找到 API 密钥')
    exit(1)

try:
    # 测试请求（Amazon 搜索，因为 Temu 支持需要确认）
    params = {
        'api_key': api_key,
        'type': 'search',
        'amazon_domain': 'amazon.com',
        'search_term': 'test'
    }
    response = requests.get('https://api.rainforestapi.com/request', params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('request_info', {}).get('success'):
            print('✅ API 连接成功！')
            print(f'📊 账户余额：{data.get(\"request_info\", {}).get(\"credits_remaining\", \"N/A\")} 次请求')
        else:
            print('⚠️  API 响应异常')
    elif response.status_code == 401:
        print('❌ API 密钥无效')
    elif response.status_code == 403:
        print('⚠️  账户余额不足或已过期')
    else:
        print(f'⚠️  响应状态码：{response.status_code}')
except Exception as e:
    print(f'❌ 测试失败：{e}')
"

echo ""
echo "================================================"
echo "  配置完成！"
echo "================================================"
echo ""
echo "下一步："
echo "1. 运行测试采集：python3 src/temu_scraper_api.py"
echo "2. 查看文档：cat docs/RAINFOREST_API_SETUP.md"
echo ""
