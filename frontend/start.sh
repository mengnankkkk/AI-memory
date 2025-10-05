#!/bin/bash

echo "🎨 启动AI灵魂伙伴 - 前端服务"
echo "================================"

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

echo "✓ 准备完成!"
echo "================================"
echo "🌐 启动Vite开发服务器..."
echo "前端地址: http://localhost:5173"
echo ""

npm run dev
