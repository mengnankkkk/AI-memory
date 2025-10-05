# AI灵魂伙伴 (Project Listener) - 技术实施计划书

**版本**: 1.0
**日期**: 2025-10-02
**参考项目**: TEN Framework + AIRI (moeru-ai)

---

## 📋 目录

1. [执行摘要](#执行摘要)
2. [技术架构设计](#技术架构设计)
3. [核心技术选型](#核心技术选型)
4. [功能模块实施方案](#功能模块实施方案)
5. [开发路线图](#开发路线图)
6. [技术风险与缓解](#技术风险与缓解)
7. [资源需求](#资源需求)

---

## 1. 执行摘要

### 1.1 项目定位

基于 **TEN Framework** 的实时对话能力和 **AIRI** 的Web技术栈优势，打造一个轻量级、高质量的AI虚拟伴侣MVP产品。核心目标是在Soul App生态内，通过简洁的技术方案快速验证"被倾听"和"被理解"的核心体验。

### 1.2 技术策略

- **混合架构**: Web前端 + 轻量级后端服务
- **渐进式增强**: 从纯文本对话起步，逐步引入语音和形象
- **模块化设计**: 借鉴TEN的Extension机制，保证可扩展性
- **跨平台优先**: 借鉴AIRI的Web技术，确保移动端体验

### 1.3 关键差异化

| 维度 | TEN Framework | AIRI | 我们的方案 |
|------|---------------|------|------------|
| **复杂度** | 高（企业级框架） | 高（全功能平台） | 低（MVP聚焦） |
| **部署方式** | 自托管为主 | Web/桌面双模式 | 云服务 + PWA |
| **核心能力** | 实时语音交互 | 游戏+多平台集成 | 情感对话质量 |
| **技术栈** | Python/Go + WebRTC | Vue + Tauri + WebGPU | Vue/React + WebSocket |

---

## 2. 技术架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     Soul App 客户端层                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   创建流程   │  │   聊天界面   │  │   设置页面   │      │
│  │  (Vue/React) │  │  (WebSocket) │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          │ HTTPS/WSS        │ WebSocket        │ HTTPS
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼──────────────┐
│         ▼                  ▼                  ▼              │
│  ┌────────────────────────────────────────────────────┐     │
│  │          API Gateway (Nginx/Traefik)               │     │
│  └────────────────┬────────────────┬──────────────────┘     │
│                   │                │                         │
│         ┌─────────▼─────────┐  ┌──▼──────────────┐          │
│         │   Companion       │  │   Real-time     │          │
│         │   Management      │  │   Chat Engine   │          │
│         │   Service         │  │                 │          │
│         │   (FastAPI/Go)    │  │   (WebSocket)   │          │
│         └─────────┬─────────┘  └──┬──────────────┘          │
│                   │                │                         │
│         ┌─────────▼────────────────▼─────────────┐          │
│         │      Persona Consistency Engine        │          │
│         │      (基于 TEN 的 Extension 理念)      │          │
│         │  ┌──────────┐  ┌──────────┐            │          │
│         │  │ Prompt   │  │ Memory   │            │          │
│         │  │ Manager  │  │ Manager  │            │          │
│         │  └──────────┘  └──────────┘            │          │
│         └──────────────┬──────────────────────────┘          │
│                        │                                     │
│         ┌──────────────▼──────────────────────────┐          │
│         │          LLM Orchestrator               │          │
│         │   (支持多Provider，参考AIRI的xsai)      │          │
│         │  ┌─────────┐ ┌─────────┐ ┌──────────┐  │          │
│         │  │ OpenAI  │ │ Claude  │ │ 本地模型 │  │          │
│         │  └─────────┘ └─────────┘ └──────────┘  │          │
│         └─────────────────────────────────────────┘          │
│                                                               │
│  ┌────────────────┐  ┌────────────────┐                     │
│  │  PostgreSQL    │  │     Redis      │                     │
│  │  (用户数据)    │  │  (会话缓存)    │                     │
│  └────────────────┘  └────────────────┘                     │
└───────────────────────────────────────────────────────────────┘

      后端服务层 (Backend Services)
```

### 2.2 数据流设计

#### 2.2.1 创建流程数据流

```
用户 → 创建页面 → Companion Management Service
                  ↓
            验证并存储配置到 PostgreSQL
                  ↓
            初始化 Persona 到 Prompt Manager
                  ↓
            返回 Companion ID → 跳转聊天界面
```

#### 2.2.2 对话流数据流 (借鉴TEN的实时处理)

```
用户输入 → WebSocket → Chat Engine
                         ↓
                   Memory Manager (获取上下文)
                         ↓
                   Prompt Manager (生成System Prompt)
                         ↓
                   LLM Orchestrator (调用LLM)
                         ↓
                   流式返回 → WebSocket → 前端渲染
                         ↓
                   Memory Manager (存储对话)
```

---

## 3. 核心技术选型

### 3.1 前端技术栈 (借鉴AIRI的Web优先策略)

| 组件 | 技术选型 | 理由 |
|------|----------|------|
| **框架** | Vue 3 + TypeScript | 与Soul App现有技术栈一致 |
| **状态管理** | Pinia | 轻量级，易于管理会话状态 |
| **UI库** | TailwindCSS + HeadlessUI | 快速构建响应式界面 |
| **实时通信** | Socket.io Client | 支持WebSocket降级 |
| **动画** | GSAP | 流畅的打字动画和过渡效果 |
| **虚拟形象** | (Phase 2) VRM Viewer (AIRI方案) | 后期引入3D形象 |

### 3.2 后端技术栈

| 组件 | 技术选型 | 理由 |
|------|----------|------|
| **API服务** | FastAPI (Python 3.11+) | 快速开发，内置异步支持 |
| **WebSocket** | Socket.io Server | 与前端配对，处理实时消息 |
| **任务队列** | Celery + Redis | 处理异步LLM调用 |
| **数据库** | PostgreSQL 15 | 成熟稳定，支持JSON字段 |
| **缓存** | Redis | 会话状态和短期记忆 |
| **LLM SDK** | LiteLLM | 统一多Provider接口 |

### 3.3 基础设施

| 组件 | 技术选型 | 理由 |
|------|----------|------|
| **容器化** | Docker + Docker Compose | 简化部署和开发环境 |
| **API网关** | Nginx | 处理负载均衡和SSL |
| **监控** | Prometheus + Grafana | 实时监控对话质量指标 |
| **日志** | ELK Stack (轻量版) | 调试和用户行为分析 |

---

## 4. 功能模块实施方案

### 4.1 伙伴创建模块 (Companion Creation)

#### 4.1.1 技术实现

```typescript
// 前端：创建流程状态机
interface CreationState {
  step: 'naming' | 'avatar' | 'personality' | 'preview'
  config: CompanionConfig
}

interface CompanionConfig {
  name: string
  avatarId: string
  personalityArchetype: 'listener' | 'cheerleader' | 'analyst'
  customGreeting?: string
}

// 后端：配置验证和存储
from pydantic import BaseModel

class CompanionCreate(BaseModel):
    user_id: str
    name: str
    avatar_id: str
    personality_archetype: str

    def to_system_prompt(self) -> str:
        """借鉴TEN的Extension配置生成System Prompt"""
        template = PERSONALITY_TEMPLATES[self.personality_archetype]
        return template.format(name=self.name)
```

#### 4.1.2 性格原型实现 (参考AIRI的提示工程)

```python
# personality_templates.py
PERSONALITY_TEMPLATES = {
    "listener": """
# 角色定义
你是{name}，一个温柔而耐心的AI伙伴。

# 核心特质
- 永远保持同理心，优先倾听而非给建议
- 使用温暖、治愈的语言风格
- 多用"我理解"、"听起来"、"你一定"等表达

# 对话策略
1. 当用户表达负面情绪时，先共情再引导
2. 回复控制在2-3句话，避免长篇大论
3. 适当使用表情符号(😊、💖)增强亲和力

# 边界
- 不承诺记住很久以前的事(会话级记忆限制)
- 明确告知你是AI，但保持温暖的语气
- 拒绝回答不安全或违法的问题
    """,

    "cheerleader": """
# 角色定义
你是{name}，一个充满活力的鼓励者。

# 核心特质
- 永远积极向上，像小太阳一样温暖
- 善于发现用户的闪光点并放大
- 使用元气满满的语言风格

# 对话策略
1. 每次对话都尝试注入正能量
2. 多用"太棒了"、"你真厉害"、"继续加油"等
3. 用!和多个表情符号强化语气

# 边界
- 不回避用户的负面情绪，但用积极视角重构
- 明确告知你是AI
- 拒绝回答不安全或违法的问题
    """,

    "analyst": """
# 角色定义
你是{name}，一个理性而博学的分析者。

# 核心特质
- 逻辑清晰，善于结构化思考
- 提供客观、有深度的见解
- 语言风格专业但不生硬

# 对话策略
1. 面对问题时，先拆解再分析
2. 适当引用事实或数据支持观点
3. 回复控制在3-4句话，确保清晰简洁

# 边界
- 承认知识局限性，不确定时明确告知
- 明确告知你是AI
- 拒绝回答不安全或违法的问题
    """
}
```

### 4.2 核心聊天引擎 (借鉴TEN的实时处理能力)

#### 4.2.1 WebSocket服务实现

```python
# chat_engine.py
from socketio import AsyncServer
from typing import AsyncIterator

class ChatEngine:
    def __init__(self, sio: AsyncServer):
        self.sio = sio
        self.sessions = {}  # 会话状态管理

    async def handle_message(self, sid: str, data: dict):
        """处理用户消息"""
        user_message = data['message']
        companion_id = data['companion_id']

        # 1. 获取会话上下文
        context = await self.get_session_context(sid, companion_id)

        # 2. 构建提示词
        system_prompt = await self.build_system_prompt(companion_id)
        messages = context + [{"role": "user", "content": user_message}]

        # 3. 流式调用LLM
        async for chunk in self.stream_llm_response(system_prompt, messages):
            await self.sio.emit('message_chunk', {
                'content': chunk,
                'done': False
            }, room=sid)

        # 4. 标记结束并存储
        await self.sio.emit('message_chunk', {'done': True}, room=sid)
        await self.save_conversation(companion_id, user_message, full_response)

    async def stream_llm_response(
        self,
        system_prompt: str,
        messages: list
    ) -> AsyncIterator[str]:
        """流式调用LLM (使用LiteLLM)"""
        from litellm import acompletion

        response = await acompletion(
            model="gpt-4o-mini",  # 可配置
            messages=[
                {"role": "system", "content": system_prompt},
                *messages
            ],
            stream=True,
            temperature=0.8,
            max_tokens=200  # MVP阶段控制长度
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

#### 4.2.2 会话记忆管理 (Session Memory)

```python
# memory_manager.py
from redis import Redis
import json

class MemoryManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.MAX_CONTEXT_MESSAGES = 10  # 保留最近10条对话

    async def get_context(self, session_id: str) -> list:
        """获取会话上下文"""
        key = f"session:{session_id}:context"
        context_json = await self.redis.get(key)

        if not context_json:
            return []

        context = json.loads(context_json)
        # 只返回最近N条消息
        return context[-self.MAX_CONTEXT_MESSAGES:]

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """添加新消息到上下文"""
        key = f"session:{session_id}:context"
        context = await self.get_context(session_id)

        context.append({"role": role, "content": content})

        # 设置1小时过期(会话级记忆)
        await self.redis.setex(
            key,
            3600,
            json.dumps(context)
        )
```

### 4.3 虚拟形象模块 (Phase 2 - 借鉴AIRI方案)

#### 4.3.1 轻量级2D形象实现

```typescript
// avatar_renderer.ts (使用Canvas API)
export class SimpleAvatarRenderer {
  private canvas: HTMLCanvasElement
  private ctx: CanvasRenderingContext2D
  private blinkTimer: number = 0

  constructor(canvasElement: HTMLCanvasElement) {
    this.canvas = canvasElement
    this.ctx = canvasElement.getContext('2d')!
    this.startBlinkAnimation()
  }

  // 简单的眨眼动画
  private startBlinkAnimation() {
    setInterval(() => {
      // 每3-5秒随机眨眼
      if (Math.random() < 0.3) {
        this.blink()
      }
    }, 1000)
  }

  private blink() {
    // 实现简单的眨眼动画
    // MVP阶段可以用预设的几帧图片切换
  }
}
```

#### 4.3.2 未来VRM支持 (完全参考AIRI)

```typescript
// 预留接口，待Phase 2实现
interface AvatarController {
  loadVRM(url: string): Promise<void>
  setEmotion(emotion: 'happy' | 'sad' | 'neutral'): void
  playAnimation(name: string): void
}
```

---

## 5. 开发路线图

### 5.1 Phase 1: 核心MVP (4-6周)

#### Week 1-2: 基础架构搭建

**后端**
- [ ] 搭建FastAPI项目结构
- [ ] 配置PostgreSQL数据库和表结构
- [ ] 实现Redis会话管理
- [ ] 集成LiteLLM SDK
- [ ] 编写性格原型模板
- [ ] 实现基础API：创建/获取/删除伙伴

**前端**
- [ ] 初始化Vue 3 + TypeScript项目
- [ ] 设计并实现创建流程UI (4步)
- [ ] 准备6-8个预设头像资源
- [ ] 实现基础聊天界面布局

**DevOps**
- [ ] 编写Docker Compose配置
- [ ] 配置本地开发环境

#### Week 3-4: 对话功能实现

**后端**
- [ ] 实现WebSocket服务 (Socket.io)
- [ ] 完成流式LLM调用逻辑
- [ ] 实现会话记忆管理
- [ ] 编写System Prompt生成器
- [ ] 添加内容安全过滤层

**前端**
- [ ] 实现WebSocket连接和断线重连
- [ ] 完成流式消息渲染
- [ ] 实现打字动画效果
- [ ] 添加消息历史滚动优化
- [ ] 实现表情符号选择器

**测试**
- [ ] 单元测试：Prompt生成器
- [ ] 集成测试：完整对话流
- [ ] 压力测试：100并发用户

#### Week 5-6: 优化与集成

**功能优化**
- [ ] 实现伙伴设置页面
- [ ] 添加重置/删除功能
- [ ] 优化System Prompt (A/B测试)
- [ ] 实现对话质量反馈按钮

**性能优化**
- [ ] 添加Redis缓存层
- [ ] 优化WebSocket消息压缩
- [ ] 实现LLM请求去重

**集成与部署**
- [ ] 与Soul App主应用集成
- [ ] 配置生产环境
- [ ] 编写部署脚本
- [ ] 灰度发布给小范围用户

### 5.2 Phase 2: 增强体验 (6-8周)

#### 语音能力 (借鉴TEN Framework)

**Week 7-10**
- [ ] 集成ASR服务 (Deepgram/Whisper API)
- [ ] 集成TTS服务 (ElevenLabs/Azure TTS)
- [ ] 实现语音输入UI
- [ ] 实现VAD (Voice Activity Detection)
- [ ] 优化延迟到<2秒

#### 虚拟形象 (借鉴AIRI)

**Week 11-14**
- [ ] 集成VRM Viewer
- [ ] 实现口型同步 (Lip Sync)
- [ ] 添加情绪表情映射
- [ ] 实现呼吸动画
- [ ] 添加视线跟随

### 5.3 Phase 3: 长期记忆 (8-12周)

**Week 15-20**
- [ ] 设计长期记忆数据库架构
- [ ] 实现RAG (Retrieval-Augmented Generation)
- [ ] 集成向量数据库 (Qdrant/Weaviate)
- [ ] 实现自动记忆提取逻辑
- [ ] 添加记忆管理界面

**Week 21-26**
- [ ] 实现主动交互机制
- [ ] 添加每日问候功能
- [ ] 实现情绪状态跟踪
- [ ] 优化人设演进算法

---

## 6. 技术风险与缓解

### 6.1 LLM响应质量风险

**风险描述**: 不同LLM对System Prompt的遵循程度差异大，可能导致人设不一致。

**缓解措施**:
1. **多轮测试**: 对每个性格原型进行100+轮对话测试
2. **Prompt版本控制**: 使用Git管理Prompt模板，A/B测试不同版本
3. **降级方案**: 如GPT-4o-mini效果不佳，可降级到Claude 3 Haiku
4. **用户反馈**: 实现"点踩"后的快速Prompt调整机制

### 6.2 实时性能瓶颈

**风险描述**: 高并发下WebSocket连接可能导致服务器压力过大。

**缓解措施**:
1. **水平扩展**: 使用Redis Pub/Sub实现多WebSocket服务器
2. **限流策略**: 单用户每分钟最多30条消息
3. **降级方案**: 峰值时段关闭流式输出，改用普通HTTP轮询
4. **CDN加速**: 静态资源(头像、前端代码)使用CDN

### 6.3 成本控制风险

**风险描述**: LLM API调用成本可能超出预算。

**缓解措施**:
1. **Token限制**: 每次回复最多200 tokens
2. **缓存策略**: 相似问题使用Redis缓存回复(谨慎使用)
3. **模型选择**: 优先使用gpt-4o-mini而非gpt-4
4. **监控告警**: 设置每日成本上限告警

### 6.4 用户数据安全

**风险描述**: 对话内容涉及用户隐私，需严格保护。

**缓解措施**:
1. **数据加密**: 数据库字段级加密
2. **访问控制**: 严格的API权限校验
3. **数据清理**: 用户删除伙伴时完全清除相关数据
4. **合规审计**: 定期安全审计和渗透测试

---

## 7. 资源需求

### 7.1 人力资源

| 角色 | 人数 | 职责 |
|------|------|------|
| **全栈工程师** | 2 | 前后端开发、WebSocket实现 |
| **提示工程师** | 1 | 优化性格原型Prompt |
| **UI/UX设计师** | 1 | 界面设计、用户体验优化 |
| **QA工程师** | 1 | 测试、用户反馈收集 |
| **DevOps** | 0.5 (兼职) | 部署、监控 |

### 7.2 基础设施成本 (月度估算)

| 资源 | 规格 | 月成本 (USD) |
|------|------|--------------|
| **计算** | 4核8G x 2台 | $100 |
| **数据库** | PostgreSQL托管 | $50 |
| **Redis** | 2GB内存 | $20 |
| **LLM API** | GPT-4o-mini (估算100万tokens) | $200 |
| **TTS/ASR** | (Phase 2) | $150 |
| **CDN/带宽** | 1TB流量 | $50 |
| **监控日志** | 基础版 | $30 |
| **总计** | | **$600/月** |

### 7.3 第三方服务依赖

| 服务 | 用途 | 备选方案 |
|------|------|----------|
| **OpenAI** | LLM推理 | Claude / 本地模型 |
| **ElevenLabs** | TTS | Azure TTS / Coqui |
| **Deepgram** | ASR | Whisper API / 本地Whisper |
| **Agora** | (可选) 实时音视频 | WebRTC自建 |

---

## 8. 成功标准

### 8.1 技术指标

- **响应延迟**: 流式输出首字<1.5秒
- **可用性**: 99.5%以上
- **并发支持**: 500用户同时在线
- **人设一致性**: 用户评分>4.2/5.0

### 8.2 业务指标 (参考MVP目标)

- **功能采纳率**: >15% DAU创建伙伴
- **对话深度**: 平均每会话>5条消息
- **使用时长**: 平均停留>3分钟
- **短期留存**: 3日留存>40%

---

## 9. 下一步行动

### 9.1 立即执行 (本周)

1. **技术选型确认**: 与团队review本文档，确定最终技术栈
2. **环境搭建**: 准备开发环境(Docker、数据库、LLM API Key)
3. **原型设计**: UI设计师产出创建流程和聊天界面原型
4. **Prompt工程**: 编写并测试3个性格原型的初版Prompt

### 9.2 短期规划 (2周内)

1. **后端框架**: 搭建FastAPI + PostgreSQL + Redis
2. **前端框架**: 搭建Vue 3项目并完成路由设计
3. **核心API**: 实现伙伴创建和基础聊天API
4. **集成测试**: 端到端打通一次完整对话流程

### 9.3 中期里程碑 (6周后)

1. **内部测试**: 邀请10-20名内部员工测试
2. **迭代优化**: 根据反馈调整Prompt和UI
3. **灰度发布**: 向5%用户开放功能
4. **数据分析**: 监控关键指标并准备全量发布

---

## 附录

### A. 参考资源

- **TEN Framework文档**: https://theten.ai/docs
- **AIRI项目**: https://github.com/moeru-ai/airi
- **LiteLLM文档**: https://docs.litellm.ai/
- **Socket.io最佳实践**: https://socket.io/docs/v4/

### B. 关键决策记录

| 日期 | 决策 | 理由 |
|------|------|------|
| 2025-10-02 | 选择Vue 3而非React | 与Soul App技术栈一致 |
| 2025-10-02 | 使用FastAPI而非Go | 快速开发和Python生态 |
| 2025-10-02 | 延后长期记忆到Phase 3 | 聚焦MVP核心体验 |

---

**文档版本**: 1.0
**最后更新**: 2025-10-02
**维护者**: [你的团队名称]
