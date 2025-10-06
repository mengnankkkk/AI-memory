#!/bin/bash

# AI恋爱攻略系统启动脚本

echo "🚀 启动 AI恋爱攻略系统..."

# 检查环境
echo "📋 检查环境依赖..."

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.8+"
    exit 1
fi

# 检查 Node.js 环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 16+"
    exit 1
fi

# 检查 Redis
if ! command -v redis-server &> /dev/null; then
    echo "⚠️  Redis 未安装，请确保 Redis 服务已启动"
fi

echo "✅ 环境检查完成"

# 启动后端服务
echo "🔧 启动后端服务..."
cd backend

# 安装 Python 依赖（如果需要）
if [ ! -d "venv" ]; then
    echo "📦 创建 Python 虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# 启动后端服务
echo "🚀 启动 FastAPI 服务器..."
python -m uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 等待后端启动
sleep 5

# 启动前端服务
echo "🎨 启动前端服务..."
cd ../frontend

# 安装前端依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动前端开发服务器
echo "🚀 启动 Vite 开发服务器..."
npm run dev &
FRONTEND_PID=$!

echo "🎉 AI恋爱攻略系统启动完成！"
echo ""
echo "📱 前端地址: http://localhost:5173"
echo "🔧 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "💖 恋爱攻略功能已集成，包括："
echo "   - 好感度系统"
echo "   - 关系阶段升级"
echo "   - AI心情变化"
echo "   - 礼物赠送"
echo "   - 每日任务"
echo "   - 随机事件"
echo "   - 记忆系统"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 保持脚本运行
wait
