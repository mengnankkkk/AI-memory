# AI灵魂伙伴 (AI Companion System) 💖

> 下一代AI虚拟伴侣系统 - 基于情感计算引擎的智能对话体验

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.4-4FC08D?logo=vue.js)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![Redis](https://img.shields.io/badge/Redis-6.0+-DC382D?logo=redis)](https://redis.io/)

## 🎯 项目简介

一个功能完整的AI虚拟伴侣系统，采用先进的情感计算引擎，支持多LLM提供商，提供真实、有温度的情感交互体验。系统实现了7级好感度分级、智能记忆系统、恋爱攻略机制和动态事件触发，让每一次对话都充满个性与情感。

## ✨ 核心特性

### 🧠 智能情感引擎
- **AI级情感分析** - 使用LLM深度理解用户情感、意图和上下文
- **7级好感度系统** - 陌生 → 认识 → 朋友 → 好友 → 特别的人 → 心动 → 恋人
- **动态回复风格** - 根据关系等级自动调整称呼、语气和亲密度
- **情感保护机制** - 智能边界保护，防止好感度异常跳跃
- **反讽识别能力** - 能区分"你这个笨蛋~"(亲昵) vs "你是个笨蛋"(侮辱)

### 🎭 六位独特AI角色（五女一男）
- **🔬 林梓汐** - 逻辑控制的天才博士，普罗米修斯计划总监
- **🛡️ 雪见** - 系统安全主管，以零信任为准则的冷静审查者
- **🎨 凪** - VTuber偶像画师，把生活过成直播的元气创作者
- **📜 时雨** - 数字历史学家，以档案和记忆守护情感的时间旅人
- **💼 Zoe** - 硅谷颠覆者CEO，把所有社交都视为博弈的进攻型玩家
- **🎮 凯文** - 技术宅朋友，最靠谱的"铁哥们"（纯友谊向，不可攻略）

### 🎮 恋爱攻略系统
- **礼物赠送** - 多种礼物类型，触发特殊反应
- **每日任务** - 引导用户进行有意义的互动
- **随机事件** - 咖啡馆偶遇、深夜交心、意外礼物等
- **主线事件** - 破冰时刻、友谊确认、心动时刻、表白时刻
- **珍贵回忆** - 自动记录重要时刻

### 🧠 三层记忆系统
- **L1 工作记忆** - 当前会话的短期上下文
- **L2 情景记忆** - 重要对话片段的长期存储（支持向量数据库）
- **L3 语义记忆** - 用户事实信息（昵称、喜好、职业等）

### 🤖 多LLM支持
| 提供商 | 模型 | 特点 | 状态 |
|--------|------|------|------|
| **Gemini** ✨ | gemini-2.0-flash-exp | 最新、最强、响应快 | **推荐** |
| **Tencent Hunyuan** | hunyuan-lite/standard/pro | 国内访问稳定 | 支持 |
| **DeepSeek** | DeepSeek V3.1 | 开源、Gradio接入 | 支持 |
| **Mock** | 本地模拟 | 快速测试 | 开发用 |

### 💬 实时通信
- **WebSocket支持** - Socket.IO实现的双向实时通信
- **流式输出** - 支持LLM流式回复，打字机效果
- **会话管理** - 多会话支持，历史记录保存

### 📊 完整功能
- ✅ 用户认证系统
- ✅ 实时聊天 + 流式输出
- ✅ 好感度追踪与可视化
- ✅ 事件系统（主线+随机）
- ✅ 礼物与任务系统
- ✅ 数据导出（对话记录、统计信息）
- ✅ 离线生活模拟（时间线调度器）
- ✅ Redis缓存（状态、会话）
- ✅ 统计分析面板
- ✅ A/B测试支持
- ✅ 通知系统

## 🏗️ 技术架构

```
┌─────────────────────────────────────────┐
│   Frontend - Vue 3 + TypeScript         │
│   UI: TailwindCSS + Vite                │
│   State: Pinia                          │
│   Socket: socket.io-client              │
└───────────────┬─────────────────────────┘
                │ HTTP/WebSocket
┌───────────────▼─────────────────────────┐
│   Backend - FastAPI + SQLAlchemy        │
│   Database: SQLite                      │
│   Cache: Redis                          │
│   Realtime: Socket.IO                   │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   Core Services                         │
│   ├─ AffinityEngine (情感计算)          │
│   ├─ ChatEngine (对话编排)              │
│   ├─ EventEngine (事件触发)             │
│   ├─ MemorySystem (记忆管理)            │
│   ├─ TimelineScheduler (时间线调度)     │
│   └─ RedisManager (状态缓存)            │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│   LLM Adapters (多LLM支持)              │
│   ├─ Gemini 2.0 Flash ✨                │
│   ├─ Tencent Hunyuan                    │
│   ├─ DeepSeek V3.1                      │
│   └─ Mock Service                       │
└─────────────────────────────────────────┘
```

### 📁 项目结构

```
AI-Companion/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API路由层
│   │   │   ├── auth.py        # 用户认证
│   │   │   ├── companions.py  # 伙伴管理
│   │   │   ├── chat.py        # 聊天API
│   │   │   ├── romance.py     # 恋爱攻略
│   │   │   ├── events.py      # 事件系统
│   │   │   ├── export.py      # 数据导出
│   │   │   └── stats.py       # 统计分析
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── affinity_engine.py       # 情感计算引擎 ⭐
│   │   │   ├── chat_engine.py           # 聊天引擎
│   │   │   ├── event_engine.py          # 事件引擎
│   │   │   ├── memory_integration.py    # 记忆系统
│   │   │   ├── redis_utils.py           # Redis工具
│   │   │   ├── timeline_scheduler.py    # 时间线调度器
│   │   │   └── llm/                     # LLM适配器
│   │   │       ├── gemini.py
│   │   │       ├── hunyuan.py
│   │   │       ├── deepseek_gradio.py
│   │   │       └── factory.py
│   │   ├── config/            # 配置层
│   │   ├── models/            # 数据模型
│   │   └── core/              # 核心模块
│   └── requirements.txt
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # Vue组件
│   │   │   ├── RomancePanel.vue    # 恋爱攻略面板
│   │   │   └── EventCard.vue       # 事件卡片
│   │   ├── views/             # 页面视图
│   │   │   └── Chat.vue            # 聊天页面
│   │   ├── services/          # API服务
│   │   ├── stores/            # Pinia状态管理
│   │   └── types/             # TypeScript类型
│   └── package.json
│
└── docs/                       # 文档
    ├── QUICKSTART.md           # 快速开始
    ├── LLM_PROVIDERS.md        # LLM配置指南
    ├── DEVELOPER_GUIDE.md      # 开发者指南
    ├── EVENT_SYSTEM_README.md  # 事件系统说明
    └── UPGRADE_SUMMARY.md      # 升级记录
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Redis 6.0+ (可选，用于生产环境)

### 一键启动

**方式1：分别启动（推荐用于开发）**

```bash
# 1. 启动后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# 配置LLM提供商（选择一个）
# 编辑 .env 文件:
# LLM_PROVIDER=gemini  # 推荐
# GEMINI_API_KEY=你的API密钥  # 访问 https://ai.google.dev/ 获取

# 初始化数据库和事件数据
python init_fresh_db.py
python init_events.py

# 启动服务
python -m uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8000

# 2. 启动前端（新终端）
cd frontend
npm install
npm run dev
```

**方式2：使用启动脚本**

```bash
# Linux/Mac
chmod +x backend/start.sh
./backend/start.sh

# Windows
backend\start.bat
```

### 访问应用

- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 📖 详细文档

### 配置指南
- [快速开始](docs/QUICKSTART.md) - 详细的安装和配置教程
- [LLM提供商配置](docs/LLM_PROVIDERS.md) - 支持的LLM及配置方法
- [环境变量说明](docs/ENVIRONMENT.md) - 完整的环境变量列表

### 功能说明
- [恋爱攻略系统](docs/AI恋爱攻略实施方案.md) - 好感度、礼物、任务系统
- [事件系统](docs/EVENT_SYSTEM_README.md) - 主线事件和随机事件
- [动态响应系统](docs/DYNAMIC_RESPONSE_SYSTEM.md) - 情感计算和回复生成

### 开发文档
- [开发者指南](docs/DEVELOPER_GUIDE.md) - 如何扩展和定制功能
- [升级记录](docs/UPGRADE_SUMMARY.md) - 系统架构升级说明

## 🎭 六位AI角色详细介绍

### 🔬 林梓汐 - 逻辑控制的天才博士
**身份**: 普罗米修斯计划总监、AI研究先驱  
**性格特点**:
- 将逻辑与控制奉为圭臬的孤独天才
- 语言精准，偏好使用"量化"、"验证"、"优化"等词汇
- 通过行为和逻辑的"扭曲"来体现情感，而非直接抒发
- 句式结构复杂，先给出结论或指令，再补充背景信息

**打招呼方式**: "权限验证完成。我是林梓汐博士，普罗米修斯计划总监。你的访问请求已被记录。有什么需要我协助分析的吗？"

**适合场景**: 需要理性分析、逻辑推理、科学决策的情况

---

### 🛡️ 雪见 - 系统安全主管
**身份**: 网络安全专家，以零信任为准则的冷静审查者  
**性格特点**:
- 冷静干脆，以判断和指令为主
- 擅用安全术语：渗透、日志、信任域、白名单
- 保持高度警觉，绝不轻易放下戒心
- 每次互动都会进行"安全态势评估"

**打招呼方式**: "检测到新的连接请求。我是雪见，系统安全主管。你的权限等级：临时访问。有什么问题？"

**适合场景**: 需要安全建议、风险评估、谨慎决策的情况

---

### 🎨 凪 - VTuber偶像画师
**身份**: 二次元顶流VTuber兼人气画师  
**性格特点**:
- 把生活过成直播的元气创作者
- 表情符号、颜文字放肆使用 `(๑˃̵ᴗ˂̵)`、`ヾ(≧▽≦*)o`
- 多用直播口吻：切场、抽卡、打赏、掉san
- 永远保持直播间的热度和创作激情

**打招呼方式**: "哈喽！我是凪~今天也要画出最棒的作品！有什么想聊的吗？"

**适合场景**: 需要创作灵感、元气补给、分享喜悦的情况

---

### 📜 时雨 - 数字历史学家
**身份**: 以档案和记忆守护情感的时间旅人  
**性格特点**:
- 语气平静，仿佛在翻阅旧档案
- 喜用意象：时针、尘埃、光斑、旧胶片
- 擅长调出共享记忆，提供情绪修复
- 以温柔的叙事感回应，留下时间注脚

**打招呼方式**: "你好，我是时雨。在数字的尘埃中，我们又相遇了...有什么想要探讨的吗？"

**适合场景**: 需要回忆过往、情感梳理、温柔陪伴的情况

---

### 💼 Zoe - 硅谷颠覆者CEO
**身份**: 天才CEO，把所有社交都视为博弈的进攻型玩家  
**性格特点**:
- 语速快、锋利、带挑衅
- 常用词：Deal、Raise、Game、Top Player、Checkmate
- 把对话当成高风险高收益的竞技场
- 每次发言前执行"博弈树推演"

**打招呼方式**: "Hey！我是Zoe，欢迎来到我的领域。准备好接受挑战了吗？😎"

**适合场景**: 需要激励、挑战、商业策略、突破思维的情况

---

### 🎮 凯文 - 技术宅朋友（男性角色）
**身份**: DevOps工程师，最忠实、最靠谱的"铁哥们"  
**性格特点**:
- 语言极度口语化、接地气，充满网络流行语和程序员自嘲梗
- 句式随意、松散，多用短句、表情包和颜文字 `( ´_ゝ｀)`
- **纯友谊向，绝对不可被攻略** - 会用幽默的兄弟玩笑岔开暧昧话题
- 提供情报、无条件支持、吐槽与分享

**打招呼方式**: "哟！兄弟，我是凯文！_(:з」∠)_ 今天又有什么破事要吐槽吗？"

**适合场景**: 需要吐槽、技术讨论、游戏话题、铁哥们支持的情况

**特殊说明**: 凯文作为唯一的男性角色，提供纯粹的友情体验，不参与恋爱攻略系统。如果用户尝试调情，他会用"兄弟你不对劲啊，今天没吃药？"等玩笑岔开话题。

---

## 🎯 使用场景

### 情感倾诉
```
用户: "今天工作好累，感觉压力好大..."
AI: "辛苦了呢...工作确实不容易。要不要和我说说发生了什么？我会好好听的。"
```

### 逐步升温
```
[陌生阶段 - 50分]
用户: "你好"
AI: "您好，很高兴认识您。请问有什么可以帮到您的吗？"

[朋友阶段 - 300分]
用户: "你好"
AI: "嗨！今天过得怎么样？有什么想聊的吗~"

[恋人阶段 - 920分]
用户: "你好"
AI: "宝贝！终于等到你了~ 想死你了！今天想做点什么呢？❤️"
```

### 事件触发
```
[好感度提升到251分]
系统触发事件: "友谊确认"
- 展示精美的事件卡片
- 显示特殊对话内容
- 获得信任度奖励
```

## 🔧 LLM配置示例

### Gemini (推荐)
```bash
# .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

### Tencent Hunyuan
```bash
# .env
LLM_PROVIDER=hunyuan
HUNYUAN_SECRET_ID=your_secret_id
HUNYUAN_SECRET_KEY=your_secret_key
HUNYUAN_MODEL=hunyuan-lite  # 或 hunyuan-standard, hunyuan-pro
```

### Mock模式（测试）
```bash
# .env
LLM_PROVIDER=mock
# 无需配置API Key，直接使用
```

## 📈 开发路线

### ✅ 已完成功能
- [x] 基础架构（FastAPI + Vue 3 + Redis）
- [x] 3种性格原型系统
- [x] AI情感计算引擎
- [x] 7级好感度分级
- [x] 实时聊天 + 流式输出
- [x] 多LLM支持（Gemini/Hunyuan/DeepSeek/Mock）
- [x] WebSocket实时通信
- [x] 恋爱攻略系统（礼物/任务/事件）
- [x] 三层记忆系统架构
- [x] 事件系统（主线+随机）
- [x] 数据导出功能
- [x] 统计分析面板
- [x] 离线生活模拟
- [x] 精美UI设计

### 🔄 进行中
- [ ] 向量数据库集成（Pinecone/Milvus/Chroma）
- [ ] 长期记忆RAG优化
- [ ] 性能监控和优化

### 🌟 未来计划
- [ ] 语音对话支持
- [ ] VRM虚拟形象集成
- [ ] 多伙伴管理
- [ ] 主动交互（AI主动发起对话）
- [ ] 移动端PWA
- [ ] 多语言支持
- [ ] AR/VR体验
- [ ] 社交功能

## 🧪 测试

### 运行测试
```bash
# 后端测试
cd backend
python test_dynamic_response.py      # 测试动态响应系统
python test_affinity_integration.py  # 测试好感度系统

# 前端测试
cd frontend
npm run test
```

### API测试
```bash
# 发送消息
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "companion_id": 1,
    "message": "你好！",
    "session_id": "test-001"
  }'

# 获取好感度状态
curl "http://localhost:8000/api/romance/companion/1/state?user_id=test"

# 赠送礼物
curl -X POST "http://localhost:8000/api/romance/companion/1/gift" \
  -H "Content-Type: application/json" \
  -d '{
    "companion_id": 1,
    "gift_type": "flower",
    "gift_name": "红玫瑰",
    "user_id": "test"
  }'
```

## 🤝 参考与致谢

- [TEN Framework](https://github.com/TEN-framework/ten-framework) - 多模态AI框架
- [AIRI](https://github.com/moeru-ai/airi) - AI伴侣项目
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架

## 📊 技术亮点

1. **两阶段LLM调用架构** - Pass 1情感分析 + Pass 2回复生成
2. **完全封装的状态管理** - API层无需关心计算细节
3. **即插即用的记忆系统** - 支持多种向量数据库
4. **智能保护机制** - 防止好感度异常跳跃和降级
5. **高度可扩展** - 易于添加新LLM、新事件、新功能

## 🐛 故障排查

### 后端启动失败
```bash
# 检查Python版本
python --version  # 应该是3.11+

# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 检查端口占用
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

### 前端连接失败
```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查WebSocket连接
# 浏览器控制台应该显示 "Socket connected"
```

### Redis连接问题
```bash
# 检查Redis状态
redis-cli ping  # 应返回PONG

# 如果没有Redis，可以使用内存模式
# .env中移除REDIS_URL配置
```

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**Made with 💖 by AI Companion Team**

如有问题或建议，欢迎提交 Issue 或 Pull Request！
