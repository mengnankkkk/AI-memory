#!/bin/bash

echo "🚀 启动AI灵魂伙伴 - 后端服务"
echo "================================"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
echo "✓ 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
if [ ! -f ".deps_installed" ]; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
    touch .deps_installed
fi

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "⚙️ 复制环境变量配置..."
    cp .env.example .env
    echo "⚠️  请检查 .env 文件并配置必要的参数"
fi

echo "✓ 准备完成!"
echo "================================"
echo "🌐 启动FastAPI服务器..."
echo "API文档: http://localhost:8000/docs"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
