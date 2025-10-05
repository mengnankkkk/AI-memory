# 环境检查脚本

## 系统要求

### 必需软件

1. **Python 3.11+**
   ```bash
   python --version
   # 应显示: Python 3.11.x 或更高
   ```

2. **Node.js 18+**
   ```bash
   node --version
   # 应显示: v18.x.x 或更高
   ```

3. **npm 或 pnpm**
   ```bash
   npm --version
   # 应显示: 9.x.x 或更高
   ```

### 可选软件

4. **Git** (用于克隆和版本管理)
   ```bash
   git --version
   ```

## 依赖说明

### 后端依赖 (已包含在requirements.txt)

所有Python依赖会在首次运行 `start.bat/start.sh` 时自动安装，无需手动操作。

**核心依赖**:
- `fastapi` - Web框架
- `uvicorn` - ASGI服务器
- `sqlalchemy` - ORM
- `aiosqlite` - 异步SQLite
- `gradio-client` - DeepSeek API调用
- `pydantic` - 数据验证
- `python-dotenv` - 环境变量

### 前端依赖 (已包含在package.json)

所有npm依赖会在首次运行 `start.bat/start.sh` 时自动安装，无需手动操作。

**核心依赖**:
- `vue` - 前端框架
- `vue-router` - 路由
- `pinia` - 状态管理
- `axios` - HTTP客户端
- `vite` - 构建工具
- `tailwindcss` - CSS框架

## 虚拟环境说明

### ✅ 自动创建 (推荐)

使用提供的启动脚本会**自动创建和管理**虚拟环境:

**Windows:**
```bash
cd backend
start.bat  # 自动创建venv并安装依赖
```

**macOS/Linux:**
```bash
cd backend
chmod +x start.sh
./start.sh  # 自动创建venv并安装依赖
```

### 🔧 手动创建 (高级用户)

如果你想手动管理:

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行应用
python -m uvicorn app.main:app --reload
```

## 环境检查清单

运行前请确认:

- [ ] Python 3.11+ 已安装
- [ ] Node.js 18+ 已安装
- [ ] 网络连接正常 (需访问Hugging Face)
- [ ] 防火墙允许8000和5173端口
- [ ] 至少2GB可用磁盘空间

## 常见问题

### Q: 是否必须使用虚拟环境?

**A: 强烈推荐**，原因:
1. 隔离项目依赖，避免版本冲突
2. 便于管理和部署
3. 启动脚本会自动处理

### Q: 能否用conda代替venv?

**A: 可以**
```bash
conda create -n ai-companion python=3.11
conda activate ai-companion
pip install -r requirements.txt
```

### Q: Windows上权限问题?

**A: 以管理员运行**
- 右键点击 `start.bat`
- 选择"以管理员身份运行"

### Q: macOS上无法执行.sh文件?

**A: 添加执行权限**
```bash
chmod +x backend/start.sh
chmod +x frontend/start.sh
```

## 完整环境测试

创建一个测试脚本:

```bash
# check_env.bat (Windows)
@echo off
echo === 环境检查 ===
echo.

echo [1/4] 检查Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python未安装
) else (
    echo ✓ Python已安装
)

echo.
echo [2/4] 检查Node.js...
node --version
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装
) else (
    echo ✓ Node.js已安装
)

echo.
echo [3/4] 检查npm...
npm --version
if %errorlevel% neq 0 (
    echo ❌ npm未安装
) else (
    echo ✓ npm已安装
)

echo.
echo [4/4] 检查Git...
git --version
if %errorlevel% neq 0 (
    echo ⚠️  Git未安装 (可选)
) else (
    echo ✓ Git已安装
)

echo.
echo === 检查完成 ===
pause
```

## 下一步

环境准备完成后:

1. **测试API**: `cd backend && python test_deepseek.py`
2. **启动后端**: `cd backend && start.bat`
3. **启动前端**: `cd frontend && start.bat` (新终端)
4. **访问应用**: `http://localhost:5173`
