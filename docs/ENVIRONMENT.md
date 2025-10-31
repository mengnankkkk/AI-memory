# 环境变量配置指南

本文档详细说明了AI灵魂伙伴系统的所有环境变量配置项。

## 📋 快速配置

### 最小配置（快速开始）

创建 `backend/.env` 文件：

```bash
# 基础配置
APP_NAME=AI灵魂伙伴
DEBUG=true

# Mock模式（无需API Key）
LLM_PROVIDER=mock
```

### 推荐配置（生产环境）

```bash
# 基础配置
APP_NAME=AI灵魂伙伴
APP_VERSION=1.0.0
DEBUG=false

# Gemini配置（推荐）
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 数据库配置
DATABASE_URL=sqlite:///./app.db

# CORS配置
ALLOWED_ORIGINS=http://localhost:5173,https://yourdomain.com

# 日志配置
LOG_LEVEL=INFO
```

---

## 🔧 完整配置项说明

### 基础配置

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `APP_NAME` | string | "AI灵魂伙伴" | 应用名称 |
| `APP_VERSION` | string | "1.0.0" | 应用版本号 |
| `DEBUG` | boolean | false | 是否启用调试模式 |
| `LOG_LEVEL` | string | "INFO" | 日志级别：DEBUG/INFO/WARNING/ERROR |

**示例：**
```bash
APP_NAME=AI灵魂伙伴
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO
```

---

### LLM提供商配置

#### 通用配置

| 变量名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `LLM_PROVIDER` | string | 是 | LLM提供商：gemini/hunyuan/deepseek_gradio/mock |

#### 1. Gemini配置 ⭐ (推荐)

| 变量名 | 类型 | 必需 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `GEMINI_API_KEY` | string | 是 | - | Google AI Studio API密钥 |
| `GEMINI_MODEL` | string | 否 | gemini-2.0-flash-exp | 模型名称 |
| `GEMINI_TEMPERATURE` | float | 否 | 0.7 | 创造性控制 (0-1) |
| `GEMINI_TOP_P` | float | 否 | 0.9 | 核采样参数 (0-1) |
| `GEMINI_MAX_TOKENS` | int | 否 | 2048 | 最大生成长度 |

**示例：**
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_TEMPERATURE=0.7
GEMINI_TOP_P=0.9
GEMINI_MAX_TOKENS=2048
```

**获取API Key:**
1. 访问 https://ai.google.dev/
2. 登录Google账号
3. 创建新的API密钥
4. 复制密钥到配置文件

#### 2. Tencent Hunyuan配置

| 变量名 | 类型 | 必需 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `HUNYUAN_SECRET_ID` | string | 是 | - | 腾讯云SecretId |
| `HUNYUAN_SECRET_KEY` | string | 是 | - | 腾讯云SecretKey |
| `HUNYUAN_MODEL` | string | 否 | hunyuan-lite | 模型：lite/standard/pro |
| `HUNYUAN_REGION` | string | 否 | ap-guangzhou | 地域 |
| `HUNYUAN_TEMPERATURE` | float | 否 | 0.7 | 创造性控制 (0-2) |
| `HUNYUAN_TOP_P` | float | 否 | 0.8 | 核采样参数 (0-1) |

**示例：**
```bash
LLM_PROVIDER=hunyuan
HUNYUAN_SECRET_ID=AKIDxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HUNYUAN_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HUNYUAN_MODEL=hunyuan-lite
HUNYUAN_REGION=ap-guangzhou
HUNYUAN_TEMPERATURE=0.7
```

**获取密钥:**
1. 访问 https://cloud.tencent.com/product/hunyuan
2. 登录腾讯云账号
3. 开通混元服务
4. 在API密钥管理中创建密钥

#### 3. DeepSeek配置

| 变量名 | 类型 | 必需 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `DEEPSEEK_API_URL` | string | 是 | - | Gradio Space地址 |

**示例：**
```bash
LLM_PROVIDER=deepseek_gradio
DEEPSEEK_API_URL=Mengnankk/deepseek-ai-DeepSeek-V3.1-test
```

#### 4. Mock模式（测试）

```bash
LLM_PROVIDER=mock
# 无需其他配置
```

---

### 数据库配置

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `DATABASE_URL` | string | sqlite:///./app.db | 数据库连接字符串 |

**SQLite示例（开发）：**
```bash
DATABASE_URL=sqlite:///./app.db
```

**PostgreSQL示例（生产）：**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/ai_companion
```

**MySQL示例（生产）：**
```bash
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/ai_companion
```

---

### Redis配置

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `REDIS_URL` | string | 可选 | Redis连接字符串 |
| `REDIS_HOST` | string | localhost | Redis主机地址 |
| `REDIS_PORT` | int | 6379 | Redis端口 |
| `REDIS_DB` | int | 0 | Redis数据库编号 |
| `REDIS_PASSWORD` | string | 可选 | Redis密码 |

**本地Redis示例：**
```bash
REDIS_URL=redis://localhost:6379/0
```

**远程Redis示例：**
```bash
REDIS_URL=redis://:password@redis.example.com:6379/0
```

**或分开配置：**
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password
```

**注意：** Redis是可选的。如果不配置，系统将使用内存存储（仅适合开发环境）。

---

### CORS配置

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `ALLOWED_ORIGINS` | string | http://localhost:5173 | 允许的跨域源，逗号分隔 |

**示例：**
```bash
# 开发环境
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# 生产环境
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

### 服务器配置

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `HOST` | string | 0.0.0.0 | 服务器监听地址 |
| `PORT` | int | 8000 | 服务器监听端口 |
| `RELOAD` | boolean | false | 是否启用热重载 |
| `WORKERS` | int | 1 | 工作进程数（生产环境） |

**开发环境示例：**
```bash
HOST=127.0.0.1
PORT=8000
RELOAD=true
WORKERS=1
```

**生产环境示例：**
```bash
HOST=0.0.0.0
PORT=8000
RELOAD=false
WORKERS=4
```

---

### 功能开关

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `ENABLE_EVENTS` | boolean | true | 是否启用事件系统 |
| `ENABLE_GIFTS` | boolean | true | 是否启用礼物系统 |
| `ENABLE_MEMORY` | boolean | true | 是否启用记忆系统 |
| `ENABLE_TIMELINE` | boolean | true | 是否启用时间线调度器 |
| `ENABLE_ANALYTICS` | boolean | true | 是否启用统计分析 |

**示例：**
```bash
ENABLE_EVENTS=true
ENABLE_GIFTS=true
ENABLE_MEMORY=true
ENABLE_TIMELINE=true
ENABLE_ANALYTICS=true
```

---

### 安全配置

| 变量名 | 类型 | 说明 |
|--------|------|------|
| `SECRET_KEY` | string | JWT签名密钥 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | 访问令牌过期时间（分钟） |

**示例：**
```bash
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7天
```

**生成安全的密钥：**
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32
```

---

## 📝 配置文件模板

### 开发环境 (.env.development)

```bash
# ==========================================
# AI灵魂伙伴 - 开发环境配置
# ==========================================

# 基础配置
APP_NAME=AI灵魂伙伴
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=DEBUG

# LLM配置（使用Mock模式快速测试）
LLM_PROVIDER=mock

# 数据库配置
DATABASE_URL=sqlite:///./app.db

# Redis配置（可选）
# REDIS_URL=redis://localhost:6379/0

# CORS配置
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# 服务器配置
HOST=127.0.0.1
PORT=8000
RELOAD=true

# 功能开关
ENABLE_EVENTS=true
ENABLE_GIFTS=true
ENABLE_MEMORY=true
ENABLE_TIMELINE=true
ENABLE_ANALYTICS=true

# 安全配置
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 生产环境 (.env.production)

```bash
# ==========================================
# AI灵魂伙伴 - 生产环境配置
# ==========================================

# 基础配置
APP_NAME=AI灵魂伙伴
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# LLM配置（使用Gemini）
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_production_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_TEMPERATURE=0.7

# 数据库配置（使用PostgreSQL）
DATABASE_URL=postgresql://user:password@db.example.com:5432/ai_companion

# Redis配置（必需）
REDIS_URL=redis://:password@redis.example.com:6379/0

# CORS配置
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 服务器配置
HOST=0.0.0.0
PORT=8000
RELOAD=false
WORKERS=4

# 功能开关
ENABLE_EVENTS=true
ENABLE_GIFTS=true
ENABLE_MEMORY=true
ENABLE_TIMELINE=true
ENABLE_ANALYTICS=true

# 安全配置（使用强密钥）
SECRET_KEY=production-secret-key-generate-a-strong-one
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

---

## 🔍 环境检查

### 自动检查脚本

创建 `check_env.py` 文件：

```python
#!/usr/bin/env python3
"""环境配置检查脚本"""

import os
import sys
from pathlib import Path

def check_env():
    """检查环境配置"""
    print("=" * 50)
    print("AI灵魂伙伴 - 环境配置检查")
    print("=" * 50)
    print()
    
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("❌ 未找到 .env 文件")
        print("📋 请复制 .env.example 并重命名为 .env")
        return False
    
    print("✅ 找到 .env 文件")
    print()
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    # 检查必需配置
    checks = {
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
        "DEBUG": os.getenv("DEBUG"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
    }
    
    all_passed = True
    
    for key, value in checks.items():
        if value:
            print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: 未配置")
            all_passed = False
    
    print()
    
    # 检查LLM特定配置
    provider = os.getenv("LLM_PROVIDER")
    
    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            print(f"✅ GEMINI_API_KEY: {'*' * 20}{api_key[-4:]}")
        else:
            print("❌ GEMINI_API_KEY: 未配置")
            all_passed = False
    
    elif provider == "hunyuan":
        secret_id = os.getenv("HUNYUAN_SECRET_ID")
        secret_key = os.getenv("HUNYUAN_SECRET_KEY")
        if secret_id and secret_key:
            print(f"✅ HUNYUAN_SECRET_ID: {secret_id[:8]}...")
            print(f"✅ HUNYUAN_SECRET_KEY: {'*' * 20}")
        else:
            print("❌ Hunyuan密钥未完整配置")
            all_passed = False
    
    elif provider == "mock":
        print("ℹ️  使用Mock模式，无需API密钥")
    
    print()
    print("=" * 50)
    
    if all_passed:
        print("✅ 环境配置检查通过")
        return True
    else:
        print("❌ 环境配置检查失败，请修正上述问题")
        return False

if __name__ == "__main__":
    sys.exit(0 if check_env() else 1)
```

运行检查：
```bash
cd backend
python check_env.py
```

---

## 🐛 常见问题

### Q1: 环境变量不生效？

**原因：**
- .env文件位置错误
- 环境变量名拼写错误
- 未重启服务

**解决：**
```bash
# 1. 确认.env文件在backend目录下
ls backend/.env

# 2. 检查文件内容
cat backend/.env

# 3. 重启后端服务
# Ctrl+C停止，然后重新启动
```

### Q2: LLM调用失败？

**检查清单：**
- [ ] LLM_PROVIDER配置正确
- [ ] API密钥正确且有效
- [ ] 网络连接正常
- [ ] API配额未用完

**测试连接：**
```bash
cd backend
python -c "
from app.services.llm.factory import llm_service
import asyncio

async def test():
    try:
        response = await llm_service.chat_completion([
            {'role': 'user', 'content': '你好'}
        ])
        print('✅ LLM连接成功:', response[:50])
    except Exception as e:
        print('❌ LLM连接失败:', e)

asyncio.run(test())
"
```

### Q3: Redis连接失败？

**检查：**
```bash
# 测试Redis连接
redis-cli ping  # 应返回PONG

# 检查Redis状态
redis-cli info server

# 测试完整连接
python -c "
import redis
r = redis.from_url('redis://localhost:6379/0')
print('✅ Redis连接成功')
"
```

**临时解决方案（开发环境）：**
```bash
# 注释掉Redis配置，使用内存存储
# REDIS_URL=redis://localhost:6379/0
```

### Q4: 数据库连接错误？

**检查：**
```bash
# 确认数据库文件存在
ls backend/app.db

# 测试连接
python -c "
from sqlalchemy import create_engine
engine = create_engine('sqlite:///./app.db')
connection = engine.connect()
print('✅ 数据库连接成功')
connection.close()
"
```

---

## 📚 下一步

配置完成后：

1. **启动系统** → [快速开始](QUICKSTART.md)
2. **切换LLM** → [LLM提供商配置](LLM_PROVIDERS.md)
3. **查看功能** → [功能清单](FEATURES.md)
4. **开始开发** → [开发者指南](DEVELOPER_GUIDE.md)

---

## 🔒 安全提醒

1. **不要提交 .env 文件到Git**
   - 已在 .gitignore 中配置
   - 仅提交 .env.example 模板

2. **使用强密钥**
   - 生产环境使用随机生成的密钥
   - 定期轮换敏感密钥

3. **保护API密钥**
   - 不要在代码中硬编码
   - 使用环境变量管理
   - 不同环境使用不同密钥

4. **限制CORS源**
   - 生产环境仅允许可信域名
   - 避免使用通配符 *

**祝配置顺利！** 🎉
