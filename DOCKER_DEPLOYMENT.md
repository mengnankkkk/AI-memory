# AI灵魂伙伴 - Docker 部署指南

## 📋 目录

- [环境要求](#环境要求)
- [快速启动](#快速启动)
- [配置说明](#配置说明)
- [服务管理](#服务管理)
- [数据持久化](#数据持久化)
- [故障排查](#故障排查)
- [备份与恢复](#备份与恢复)
- [性能优化](#性能优化)
- [安全建议](#安全建议)

---

## 🔧 环境要求

### 必需软件

- **Docker**: 版本 20.10 或更高
- **Docker Compose**: 版本 2.0 或更高
- **系统资源**:
  - CPU: 2核心或以上
  - 内存: 4GB 或以上
  - 磁盘: 10GB 可用空间

### 验证安装

```bash
# 检查 Docker 版本
docker --version

# 检查 Docker Compose 版本
docker-compose --version
```

---

## 🚀 快速启动

### 1. 克隆项目（如果还没有）

```bash
git clone <repository-url>
cd AI-memory
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp backend/.env.production backend/.env

# 编辑环境变量，填入你的 API 密钥
# Windows 使用: notepad backend/.env
# Linux/Mac 使用: nano backend/.env
nano backend/.env
```

**必须配置的变量**：

- `LLM_PROVIDER`: 选择 LLM 提供商（推荐 `hunyuan` 或 `gemini`）
- `GEMINI_API_KEY`: 如果使用 Gemini（从 https://ai.google.dev/ 获取）
- `HUNYUAN_SECRET_ID` / `HUNYUAN_SECRET_KEY`: 如果使用腾讯混元（从 https://console.cloud.tencent.com/ 获取）
- `ALLOWED_ORIGINS`: 添加你的域名（如果有）

### 3. 创建必要的目录

```bash
# 创建数据目录
mkdir -p backend/data backend/chroma_db

# 确保 img 目录存在且包含静态资源
ls -la img/
```

### 4. 构建并启动服务

```bash
# 构建镜像并启动所有服务
docker-compose up -d --build

# 查看启动日志
docker-compose logs -f
```

### 5. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 测试后端健康检查
curl http://localhost:8000/health

# 测试前端
curl http://localhost/
```

访问 http://localhost 即可使用应用！

---

## ⚙️ 配置说明

### 架构概览

```
┌─────────────┐
│   用户浏览器  │
└──────┬──────┘
       │ http://localhost
       ↓
┌─────────────────┐
│  Frontend (Nginx)│  端口: 80
│  - 静态文件服务   │
│  - API 反向代理   │
└────────┬────────┘
         │ /api, /socket.io
         ↓
┌─────────────────┐
│  Backend (FastAPI)│ 端口: 8000
│  - RESTful API   │
│  - WebSocket     │
└────┬──────┬─────┘
     │      │
     │      └─────────┐
     ↓                ↓
┌─────────┐    ┌──────────┐
│  Redis  │    │  SQLite  │
│  缓存    │    │  数据库   │
└─────────┘    └──────────┘
```

### 服务说明

#### 1. Redis (缓存服务)

- **端口**: 6379
- **用途**: 缓存热点数据、会话存储
- **持久化**: 使用 AOF（Append Only File）

#### 2. Backend (后端服务)

- **端口**: 8000
- **技术栈**: FastAPI + Python 3.11
- **功能**:
  - RESTful API
  - WebSocket 实时通信
  - LLM 集成
  - 数据库操作

#### 3. Frontend (前端服务)

- **端口**: 80
- **技术栈**: Vue 3 + Vite + Nginx
- **功能**:
  - 静态文件服务
  - API 反向代理
  - WebSocket 代理

### 环境变量详解

#### LLM 配置

```bash
# 选择 LLM 提供商
LLM_PROVIDER=hunyuan  # 可选: gemini, hunyuan, new_gradio, mock

# Gemini 配置
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# 腾讯混元配置
HUNYUAN_SECRET_ID=your_id_here
HUNYUAN_SECRET_KEY=your_key_here
HUNYUAN_MODEL=hunyuan-turbo
```

#### 数据库配置

```bash
# SQLite 数据库路径（容器内）
DATABASE_URL=sqlite+aiosqlite:///./data/ai_companion.db

# Redis 连接
REDIS_URL=redis://redis:6379/0
```

#### 应用配置

```bash
# 应用名称和版本
APP_NAME=AI灵魂伙伴
APP_VERSION=1.0.0

# 调试模式（生产环境设为 False）
DEBUG=False

# CORS 允许的源
ALLOWED_ORIGINS=http://localhost,http://your-domain.com
```

---

## 🎛️ 服务管理

### 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose stop

# 重启所有服务
docker-compose restart

# 停止并删除所有容器
docker-compose down

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f redis

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh

# 重新构建镜像
docker-compose build --no-cache

# 更新并重启服务
docker-compose up -d --build
```

### 单独管理服务

```bash
# 只启动后端和 Redis
docker-compose up -d redis backend

# 重启前端
docker-compose restart frontend

# 查看后端资源使用
docker stats ai-companion-backend
```

---

## 💾 数据持久化

### 数据卷说明

项目使用以下方式持久化数据：

#### 1. Redis 数据

```yaml
volumes:
  - redis_data:/data  # Docker 管理的 volume
```

#### 2. SQLite 数据库

```yaml
volumes:
  - ./backend/data:/app/data  # 宿主机目录挂载
```

数据库文件位置: `backend/data/ai_companion.db`

#### 3. ChromaDB 向量数据

```yaml
volumes:
  - ./backend/chroma_db:/app/chroma_db
```

#### 4. 静态资源（图片/视频）

```yaml
volumes:
  - ./img:/app/img:ro  # 只读挂载
```

### 查看数据卷

```bash
# 列出所有 volume
docker volume ls

# 查看 Redis volume 详情
docker volume inspect ai-memory_redis_data

# 查看 volume 占用空间
docker system df -v
```

---

## 🔍 故障排查

### 1. 服务无法启动

#### 检查端口占用

```bash
# Windows
netstat -ano | findstr :80
netstat -ano | findstr :8000
netstat -ano | findstr :6379

# Linux/Mac
lsof -i :80
lsof -i :8000
lsof -i :6379
```

#### 修改端口映射

编辑 `docker-compose.yml`：

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # 将前端改为 8080 端口
```

### 2. 后端启动失败

#### 查看详细日志

```bash
docker-compose logs backend
```

#### 常见问题

**问题**: `ModuleNotFoundError`

```bash
# 重新构建镜像
docker-compose build --no-cache backend
```

**问题**: 数据库文件权限错误

```bash
# 修复权限
chmod 755 backend/data
chmod 644 backend/data/ai_companion.db
```

**问题**: API Key 无效

```bash
# 检查环境变量
docker-compose exec backend env | grep API_KEY
```

### 3. 前端无法连接后端

#### 检查网络连通性

```bash
# 进入前端容器
docker-compose exec frontend sh

# 测试后端连接
wget -O- http://backend:8000/health
```

#### 检查 Nginx 配置

```bash
# 查看 Nginx 配置
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# 测试 Nginx 配置
docker-compose exec frontend nginx -t

# 重新加载 Nginx
docker-compose exec frontend nginx -s reload
```

### 4. WebSocket 连接失败

#### 检查 Socket.IO 日志

```bash
docker-compose logs backend | grep socket
```

#### 检查浏览器控制台

打开浏览器开发者工具 (F12)，查看 Network 标签下的 WebSocket 连接状态。

#### 确认 Nginx 配置

`frontend/nginx.conf` 中的 WebSocket 配置：

```nginx
location /socket.io/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### 5. Redis 连接失败

#### 检查 Redis 状态

```bash
# 测试 Redis 连接
docker-compose exec redis redis-cli ping
# 应该返回: PONG

# 查看 Redis 信息
docker-compose exec redis redis-cli info
```

#### 从后端测试 Redis

```bash
docker-compose exec backend python -c "
import redis
r = redis.from_url('redis://redis:6379/0')
print(r.ping())
"
```

### 6. 磁盘空间不足

#### 清理 Docker 资源

```bash
# 查看磁盘使用
docker system df

# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的 volume
docker volume prune

# 一键清理所有未使用资源
docker system prune -a --volumes
```

---

## 🔄 备份与恢复

### 备份数据

#### 1. 备份 SQLite 数据库

```bash
# 创建备份目录
mkdir -p backups

# 备份数据库
docker-compose exec backend sqlite3 /app/data/ai_companion.db ".backup /app/data/backup.db"

# 复制到宿主机
cp backend/data/backup.db backups/ai_companion_$(date +%Y%m%d_%H%M%S).db
```

#### 2. 备份 ChromaDB

```bash
# 打包 ChromaDB 数据
tar -czf backups/chroma_db_$(date +%Y%m%d_%H%M%S).tar.gz backend/chroma_db/
```

#### 3. 备份 Redis 数据

```bash
# 触发 Redis 保存
docker-compose exec redis redis-cli BGSAVE

# 复制 RDB 文件
docker cp ai-companion-redis:/data/dump.rdb backups/redis_$(date +%Y%m%d_%H%M%S).rdb
```

#### 4. 完整备份脚本

创建 `backup.sh`：

```bash
#!/bin/bash

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "开始备份..."

# 备份数据库
echo "备份 SQLite 数据库..."
cp backend/data/ai_companion.db "$BACKUP_DIR/"

# 备份 ChromaDB
echo "备份 ChromaDB..."
tar -czf "$BACKUP_DIR/chroma_db.tar.gz" backend/chroma_db/

# 备份 Redis
echo "备份 Redis..."
docker-compose exec -T redis redis-cli BGSAVE
sleep 2
docker cp ai-companion-redis:/data/dump.rdb "$BACKUP_DIR/redis.rdb"

# 备份配置
echo "备份配置文件..."
cp backend/.env "$BACKUP_DIR/"
cp docker-compose.yml "$BACKUP_DIR/"

echo "备份完成！位置: $BACKUP_DIR"
```

### 恢复数据

#### 1. 恢复 SQLite 数据库

```bash
# 停止服务
docker-compose stop backend

# 恢复数据库
cp backups/ai_companion_20250103_120000.db backend/data/ai_companion.db

# 重启服务
docker-compose start backend
```

#### 2. 恢复 ChromaDB

```bash
# 停止服务
docker-compose stop backend

# 删除旧数据
rm -rf backend/chroma_db/*

# 解压备份
tar -xzf backups/chroma_db_20250103_120000.tar.gz -C backend/

# 重启服务
docker-compose start backend
```

#### 3. 恢复 Redis

```bash
# 停止 Redis
docker-compose stop redis

# 复制 RDB 文件
docker cp backups/redis_20250103_120000.rdb ai-companion-redis:/data/dump.rdb

# 重启 Redis
docker-compose start redis
```

---

## ⚡ 性能优化

### 1. 资源限制

编辑 `docker-compose.yml`，为服务添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 2. Redis 优化

```yaml
redis:
  command: >
    redis-server
    --appendonly yes
    --maxmemory 512mb
    --maxmemory-policy allkeys-lru
```

### 3. Nginx 缓存

在 `frontend/nginx.conf` 中启用缓存：

```nginx
# 静态资源缓存
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|webp|mp4)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 4. 日志轮转

限制 Docker 日志大小：

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 🔒 安全建议

### 1. 环境变量安全

```bash
# 不要将 .env 文件提交到 Git
echo "backend/.env" >> .gitignore

# 使用 Docker Secrets（Swarm 模式）
docker secret create gemini_key ./gemini_key.txt
```

### 2. 网络隔离

```yaml
services:
  redis:
    # 不暴露到宿主机
    # ports:
    #   - "6379:6379"
    expose:
      - "6379"
```

### 3. 使用非 root 用户

在 Dockerfile 中添加：

```dockerfile
# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser
```

### 4. 定期更新镜像

```bash
# 拉取最新基础镜像
docker-compose pull

# 重新构建
docker-compose build --no-cache

# 重启服务
docker-compose up -d
```

### 5. 启用 HTTPS

使用 Nginx + Let's Encrypt：

```bash
# 安装 Certbot
apt-get install certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d your-domain.com
```

---

## 📊 监控和日志

### 查看实时日志

```bash
# 所有服务
docker-compose logs -f --tail=100

# 特定服务
docker-compose logs -f backend --tail=50
```

### 查看资源使用

```bash
# 实时监控
docker stats

# 查看特定容器
docker stats ai-companion-backend
```

### 导出日志

```bash
# 导出日志到文件
docker-compose logs backend > logs/backend_$(date +%Y%m%d).log
```

---

## 🆘 获取帮助

如果遇到问题：

1. 查看日志: `docker-compose logs -f`
2. 检查服务状态: `docker-compose ps`
3. 查看健康检查: `docker inspect ai-companion-backend | grep Health`
4. 搜索 GitHub Issues
5. 提交新的 Issue（附带日志和配置信息）

---

## 📝 更新日志

### v1.0.0 (2025-01-03)

- ✅ 初始 Docker 部署方案
- ✅ 支持 Redis 缓存
- ✅ 支持多 LLM 提供商
- ✅ 前后端分离架构
- ✅ 健康检查和自动重启
- ✅ 数据持久化
