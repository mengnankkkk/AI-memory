@echo off
echo 🚀 启动AI灵魂伙伴 - 后端服务
echo ================================

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo ✓ 激活虚拟环境...
call venv\Scripts\activate

REM 安装依赖
if not exist ".deps_installed" (
    echo 📦 安装依赖...
    pip install -r requirements.txt
    type nul > .deps_installed
)

REM 检查环境变量
if not exist ".env" (
    echo ⚙️ 复制环境变量配置...
    copy .env.example .env
    echo ⚠️  请检查 .env 文件并配置必要的参数
)

echo ✓ 准备完成!
echo ================================

REM 初始化Redis配置
echo 🔧 初始化Redis配置...
python init_redis_config.py

echo 🌐 启动FastAPI服务器...
echo API文档: http://localhost:8000/docs
echo.

python -m uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8000

pause
