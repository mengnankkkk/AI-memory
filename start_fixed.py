#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI灵魂伙伴 - 统一启动脚本 (Windows优化版)
同时启动后端和前端服务
"""
import os
import sys
import subprocess
import time
import platform
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

# 控制台颜色
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color):
    """打印彩色文本"""
    if platform.system() == "Windows":
        # Windows下直接打印，不使用颜色
        print(text)
    else:
        print(f"{color}{text}{Colors.RESET}")

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_python():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("[X] Python版本需要 3.11+")
        sys.exit(1)
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")

def check_node():
    """检查Node.js"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, shell=True)
        print(f"[OK] Node.js {result.stdout.strip()}")
    except Exception:
        print("[X] Node.js未安装")
        sys.exit(1)

def setup_backend():
    """设置后端环境"""
    print_header("设置后端环境")

    os.chdir(BACKEND_DIR)

    # 检查虚拟环境
    venv_dir = BACKEND_DIR / "venv"
    if not venv_dir.exists():
        print("[1/3] 创建虚拟环境...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    else:
        print("[1/3] 虚拟环境已存在")

    # 获取pip路径
    if platform.system() == "Windows":
        pip_path = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_path = venv_dir / "bin" / "pip"

    # 安装依赖
    print("[2/3] 安装依赖...")
    subprocess.run([str(pip_path), "install", "-q", "-r", "requirements.txt"], check=True)

    # 创建.env
    env_file = BACKEND_DIR / ".env"
    if not env_file.exists():
        print("[3/3] 创建.env文件...")
        import shutil
        shutil.copy(".env.example", ".env")
    else:
        print("[3/3] .env文件已存在")

    print("[OK] 后端环境设置完成")

def setup_frontend():
    """设置前端环境"""
    print_header("设置前端环境")

    os.chdir(FRONTEND_DIR)

    # 检查node_modules
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("[1/1] 安装依赖...")
        subprocess.run("npm install", shell=True, check=True)
    else:
        print("[1/1] 依赖已安装")

    print("[OK] 前端环境设置完成")

def start_backend():
    """启动后端服务"""
    os.chdir(BACKEND_DIR)

    # 获取Python路径
    if platform.system() == "Windows":
        python_path = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    else:
        python_path = BACKEND_DIR / "venv" / "bin" / "python"

    print("\n[Backend] 启动后端服务...")
    print("   API地址: http://localhost:8000")
    print("   API文档: http://localhost:8000/docs\n")

    # 启动uvicorn
    return subprocess.Popen([
        str(python_path), "-m", "uvicorn",
        "app.main:socket_app",  # 使用socket_app而不是app
        "--reload",
        "--host", "127.0.0.1",
        "--port", "8000"
    ])

def start_frontend():
    """启动前端服务"""
    os.chdir(FRONTEND_DIR)

    print("\n[Frontend] 启动前端服务...")
    print("   前端地址: http://localhost:5173\n")

    # 启动vite (Windows使用shell=True)
    return subprocess.Popen("npm run dev", shell=True)

def main():
    """主函数"""
    try:
        print_header("AI灵魂伙伴 - 启动程序")

        # 环境检查
        print("📋 环境检查")
        check_python()
        check_node()

        # 设置环境
        setup_backend()
        setup_frontend()

        # 启动服务
        print_header("启动服务")

        backend_process = start_backend()
        time.sleep(3)  # 等待后端启动

        frontend_process = start_frontend()
        time.sleep(2)  # 等待前端启动

        print_header("服务已启动")
        print("[OK] 后端: http://localhost:8000")
        print("[OK] 前端: http://localhost:5173")
        print("\n按 Ctrl+C 停止所有服务\n")

        # 等待中断
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n\n正在停止服务...")
            backend_process.terminate()
            frontend_process.terminate()

            time.sleep(1)

            backend_process.kill()
            frontend_process.kill()

            print("[OK] 所有服务已停止")

    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
