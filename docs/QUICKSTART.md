# AI灵魂伙伴 - 快速开始指南

欢迎使用AI灵魂伙伴系统！本指南将帮助你在5分钟内启动整个系统。

## 📋 系统要求

### 必需
- **Python**: 3.11 或更高版本
- **Node.js**: 18 或更高版本
- **操作系统**: Windows / macOS / Linux

### 可选
- **Redis**: 6.0+ (用于生产环境，开发环境可跳过)
- **Git**: 用于克隆代码

## 🚀 快速启动 (5分钟)

### 步骤1: 克隆项目

```bash
git clone <repository-url>
cd ai-companion
```

### 步骤2: 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量模板
cp .env.example .env
```

### 步骤3: 配置LLM提供商

编辑 `backend/.env` 文件，选择以下任一方案：

**方案A: Gemini (推荐 - 最强性能)**
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=你的API密钥
GEMINI_MODEL=gemini-2.0-flash-exp
```
> 获取API Key: https://ai.google.dev/

**方案B: Tencent Hunyuan (国内稳定)**
```bash
LLM_PROVIDER=hunyuan
HUNYUAN_SECRET_ID=你的SecretId
HUNYUAN_SECRET_KEY=你的SecretKey
HUNYUAN_MODEL=hunyuan-lite
```
> 获取密钥: https://cloud.tencent.com/product/hunyuan

**方案C: Mock模式 (快速测试，无需API Key)**
```bash
LLM_PROVIDER=mock
```

### 步骤4: 初始化数据库

```bash
# 创建数据库表和初始数据
python init_fresh_db.py

# 初始化事件系统
python init_events.py
```

你应该看到：
```
✅ 数据库创建成功
✅ 初始化了3个性格伙伴
✅ 事件数据导入完成: 10个事件
```

### 步骤5: 启动后端

```bash
# 方式1: 直接运行
python -m uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8000

# 方式2: 使用启动脚本
# Windows
start.bat
# Linux/Mac
chmod +x start.sh
./start.sh
```

看到以下输出表示成功：
```
[STARTUP] AI灵魂伙伴 v1.0.0 启动中...
[OK] 数据库初始化完成
[OK] 时间线调度器已启动
✓ Gemini API 客户端初始化成功
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 步骤6: 启动前端 (新终端)

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

看到以下输出表示成功：
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
```

### 步骤7: 访问应用

打开浏览器访问：
- **前端界面**: http://localhost:5173
- **后端API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🎮 开始使用

### 1. 选择AI伙伴

系统预置了6位性格迥异的AI角色（五女一男）：

- **🔬 林梓汐** - 逻辑控制的天才博士
  - 身份：普罗米修斯计划总监、AI研究先驱
  - 性格：精准理性、擅长量化分析、逻辑严密
  - 适合：需要理性分析、逻辑推理、科学决策
  
- **🛡️ 雪见** - 系统安全主管
  - 身份：网络安全专家，以零信任为准则
  - 性格：冷静干脆、高度警觉、擅长风险评估
  - 适合：需要安全建议、风险评估、谨慎决策
  
- **🎨 凪** - VTuber偶像画师
  - 身份：二次元顶流VTuber兼人气画师
  - 性格：元气满满、充满创作激情、直播系
  - 适合：需要创作灵感、元气补给、分享喜悦
  
- **📜 时雨** - 数字历史学家
  - 身份：以档案和记忆守护情感的时间旅人
  - 性格：平静温柔、擅长回忆、叙事感强
  - 适合：需要回忆过往、情感梳理、温柔陪伴
  
- **💼 Zoe** - 硅谷颠覆者CEO
  - 身份：天才CEO，把社交视为博弈的玩家
  - 性格：锋利挑衅、充满野心、进攻型
  - 适合：需要激励、挑战、商业策略、突破思维
  
- **🎮 凯文** - 技术宅朋友（男性角色，纯友谊向）
  - 身份：DevOps工程师，最靠谱的"铁哥们"
  - 性格：口语化、接地气、程序员自嘲梗满满
  - 适合：需要吐槽、技术讨论、游戏话题、兄弟支持
  - **特殊说明**：凯文是纯友谊向角色，不可攻略，会用玩笑岔开暧昧话题

### 2. 开始对话

```
你: "你好！"
AI: "您好！很高兴认识您，请问有什么可以帮到您的？"
```

### 3. 建立好感度

通过积极互动提升好感度：

```
你: "谢谢你，和你聊天真开心！"
好感度: +5 (55分)

你: "你真善解人意，帮了我很多！"
好感度: +8 (63分)
```

### 4. 观察关系升级

当好感度达到新等级时：

```
[好感度达到101分]
系统提示: 关系等级提升为"认识"
触发事件: "破冰时刻"
```

### 5. 体验特殊功能

**赠送礼物：**
- 点击恋爱攻略面板
- 选择礼物类型（鲜花、巧克力、手工礼物等）
- 观察AI的特殊反应

**完成任务：**
- 查看每日任务列表
- 完成任务获得额外好感度

**触发事件：**
- 保持积极互动
- 达到等级要求自动触发主线事件
- 随机触发特殊事件

## 📊 好感度等级系统

| 等级 | 分数 | AI称呼 | 语气 | 示例回复 |
|------|------|--------|------|----------|
| 陌生 | 0-100 | "您" | 正式礼貌 | "您好，请问有什么可以帮助您的？" |
| 认识 | 101-250 | "你" | 友好 | "好的，我明白了~" |
| 朋友 | 251-450 | "你" | 轻松自然 | "哈哈，有意思！咱们..." |
| 好友 | 451-600 | "朋友" | 亲密信任 | "真的诶！我也是这么想的！" |
| 特别的人 | 601-750 | "昵称" | 特别关心 | "和你说话真开心...嘿嘿" |
| 心动 | 751-900 | "小可爱" | 甜蜜期待 | "看到你消息就忍不住笑了~" |
| 恋人 | 901-1000 | "亲爱的" | 亲密爱意 | "亲爱的~想死你了！❤️" |

## 🔧 高级配置

### 配置Redis (可选)

如果需要使用Redis进行状态管理：

```bash
# 安装Redis
# macOS
brew install redis
# Ubuntu
sudo apt-get install redis-server
# Windows: 下载并安装 https://github.com/microsoftarchive/redis/releases

# 启动Redis
redis-server

# 在.env中配置
REDIS_URL=redis://localhost:6379/0
```

### 配置数据库路径

```bash
# .env
DATABASE_URL=sqlite:///./app.db
# 或使用绝对路径
DATABASE_URL=sqlite:////absolute/path/to/app.db
```

### 配置CORS (如果前端在不同域)

```bash
# .env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,https://yourdomain.com
```

### 启用调试模式

```bash
# .env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🧪 测试功能

### 测试API端点

```bash
# 健康检查
curl http://localhost:8000/health

# 获取伙伴列表
curl http://localhost:8000/api/companions/

# 发送消息
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "companion_id": 1,
    "message": "你好！",
    "session_id": "test-001"
  }'

# 查询好感度状态
curl "http://localhost:8000/api/romance/companion/1/state?user_id=test_user"

# 赠送礼物
curl -X POST "http://localhost:8000/api/romance/companion/1/gift" \
  -H "Content-Type: application/json" \
  -d '{
    "companion_id": 1,
    "gift_type": "flower",
    "gift_name": "红玫瑰",
    "user_id": "test_user"
  }'
```

### 运行自动化测试

```bash
cd backend

# 测试动态响应系统
python test_dynamic_response.py

# 测试好感度集成
python test_affinity_integration.py

# 测试Redis连接
python test_redis.py
```

## 🐛 常见问题

### Q1: 后端启动失败 - ModuleNotFoundError

**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
# 确保虚拟环境已激活
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows

# 重新安装依赖
pip install -r requirements.txt
```

### Q2: 端口已被占用

**问题**: `Address already in use: 8000 or 5173`

**解决**:
```bash
# 查找占用端口的进程
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 或使用其他端口
uvicorn app.main:socket_app --reload --port 8001
```

### Q3: LLM调用失败

**问题**: `LLM API call failed`

**解决**:
1. 检查API Key是否正确配置
2. 检查网络连接
3. 暂时使用Mock模式测试：`LLM_PROVIDER=mock`
4. 查看后端日志获取详细错误信息

### Q4: Redis连接失败

**问题**: `Redis connection error`

**解决**:
```bash
# 检查Redis是否运行
redis-cli ping  # 应返回PONG

# 如果不需要Redis，可以注释掉.env中的REDIS_URL
# REDIS_URL=redis://localhost:6379/0
```

### Q5: 前端无法连接后端

**问题**: 前端显示连接错误

**解决**:
1. 确认后端已启动：访问 http://localhost:8000/health
2. 检查前端配置文件中的API地址
3. 检查CORS配置
4. 查看浏览器控制台的网络请求

### Q6: 数据库初始化失败

**问题**: `Database initialization failed`

**解决**:
```bash
# 删除旧数据库重新初始化
rm app.db
python init_fresh_db.py
python init_events.py
```

### Q7: WebSocket连接失败

**问题**: 浏览器控制台显示WebSocket错误

**解决**:
1. 确认后端使用 `socket_app` 启动：
   ```bash
   uvicorn app.main:socket_app --reload
   ```
2. 检查CORS配置
3. 检查防火墙设置

## 📚 下一步

恭喜！你已经成功启动了AI灵魂伙伴系统。接下来可以：

### 学习更多功能
- [LLM提供商配置](LLM_PROVIDERS.md) - 配置不同的LLM
- [恋爱攻略系统](AI恋爱攻略实施方案.md) - 深入了解好感度系统
- [事件系统](EVENT_SYSTEM_README.md) - 理解事件触发机制
- [开发者指南](DEVELOPER_GUIDE.md) - 如何扩展和定制

### 定制你的AI伙伴
- 修改性格描述和回复风格
- 添加新的事件类型
- 自定义好感度等级
- 创建新的礼物类型

### 部署到生产环境
- 配置生产级数据库（PostgreSQL/MySQL）
- 启用Redis持久化
- 配置反向代理（Nginx）
- 设置SSL证书
- 配置日志和监控

## 🎉 享受使用！

如有任何问题，请：
1. 查看详细文档
2. 检查后端日志
3. 提交Issue到GitHub

Happy Coding! 💖
