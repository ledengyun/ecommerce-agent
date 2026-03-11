#!/bin/bash
# GitHub 推送脚本
# 在本地网络好的机器上运行

set -e

REPO_URL="https://github.com/ledengyun/ecommerce-agent.git"
USERNAME="ledengyun"

echo "🚀 推送到 GitHub: $REPO_URL"
echo ""

# 检查 git 是否已配置
if ! git config user.name > /dev/null 2>&1; then
    echo "⚙️  配置 git 用户信息..."
    git config user.name "ledengyun"
    git config user.email "ledengyun@126.com"
fi

# 添加远程仓库（如果还没有）
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "🔗 添加远程仓库..."
    git remote add origin $REPO_URL
fi

# 推送代码
echo "📤 推送到 GitHub..."
echo "提示：可能需要输入 GitHub 密码或 Personal Access Token"
echo ""

git push -u origin master

echo ""
echo "✅ 推送完成！"
echo "📍 查看仓库：https://github.com/ledengyun/ecommerce-agent"
