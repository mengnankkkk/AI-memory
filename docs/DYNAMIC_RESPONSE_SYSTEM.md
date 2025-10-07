# 动态回复系统 - 集成文档

## 📚 系统概述

动态回复系统是一个基于用户好感度的智能回复生成系统，能够根据用户与AI的互动历史，自动调整AI的回复风格、语气和内容，创造更真实、更有层次感的对话体验。

## 🏗️ 系统架构

```
动态回复系统
├── 配置层 (app/config/)
│   ├── affinity_levels.py      # 好感度等级配置
│   └── response_rules.py       # 回复规则配置
│
├── 服务层 (app/services/)
│   ├── content_detector.py     # 内容检测机制
│   ├── affinity_protector.py   # 容错保护机制
│   └── dynamic_response_system.py  # 系统核心
│
└── 应用层 (app/api/)
    └── chat.py                 # 聊天API(已集成)
```

## 🎯 核心功能

### 1. 好感度分级系统 (7个等级)

| 等级 | 分数范围 | 描述 | 回复风格 |
|------|----------|------|----------|
| 陌生 | 0-100 | 刚刚认识 | 正式、礼貌、有距离感 |
| 认识 | 101-250 | 初步了解 | 半正式、友好 |
| 朋友 | 251-450 | 建立友谊 | 轻松、自然、幽默 |
| 好友 | 451-600 | 深入了解 | 亲密、信任、默契 |
| 特别的人 | 601-750 | 微妙情感 | 特殊关心、暗示 |
| 心动 | 751-900 | 萌芽爱意 | 甜蜜、期待、心动 |
| 恋人 | 901-1000 | 确认关系 | 亲密、爱意、甜蜜 |

### 2. 内容检测机制

**检测维度:**
- ✅ 情感分析 (积极/消极/浪漫)
- ✅ 行为类型 (问候/分享/提问/请求)
- ✅ 合适性检查 (是否符合当前等级)
- ✅ 禁忌词检测 (根据等级动态调整)

**好感度调整规则:**
```python
# 增加规则
赞美 → +2至+10分 (根据等级递增)
分享 → +1至+8分
感谢 → +1至+5分
长消息 → 额外+1至+7分

# 减少规则
侮辱 → -20分
愤怒 → -10分
抱怨 → -5分
不当亲密 → -5至-10分 (等级不符)
```

### 3. 容错保护机制

**边界保护:**
- 绝对范围: 0-1000分
- 安全范围: 50-950分
- 单次最大增加: 50分
- 单次最大减少: 30分

**速率调整:**
- 低分保护 (<50): 负面影响减少70%，正面提升加速20%
- 高分减速 (>950): 正面增长减少30%
- 快速变化检测: 5分钟内变化>100分，触发保护

**历史追踪:**
- 保留最近20条互动记录
- 趋势分析 (上升/下降/稳定/波动)
- 恢复建议

### 4. 回复规则引擎

每个等级配置包含:
- **称呼方式**: 从"您"到"亲爱的"的渐进
- **语气词**: 句尾语气词库
- **表情符号**: 使用频率和类型
- **消息长度**: 偏好设置
- **禁忌词**: 该等级不应使用的词汇
- **话题建议**: 可主动提起的话题

## 🔧 集成说明

### 主应用集成点 (chat.py)

系统已完全集成到 `/api/chat` 端点:

```python
# 1. 处理用户消息
process_result = dynamic_response_system.process_user_message(
    user_message=request.message,
    current_affinity_score=current_affinity_score,
    user_id=companion.user_id,
    companion_id=request.companion_id,
    current_mood=current_mood
)

# 2. 更新好感度
affinity_change = process_result["affinity_change"]["adjusted_change"]
await redis_affinity_manager.update_affinity(...)

# 3. 增强系统提示词
enhanced_system_prompt = dynamic_response_system.get_system_prompt_enhancement(
    base_system_prompt,
    level,
    mood,
    affinity_score
)

# 4. 调整AI回复
adjusted_response = dynamic_response_system.generate_ai_response(
    llm_response,
    process_result["response_guidance"]
)
```

### 数据流程

```
用户消息
  ↓
内容检测 (情感、行为、合适性)
  ↓
保护机制 (调整好感度变化)
  ↓
更新状态 (分数、等级)
  ↓
生成指导 (回复规则、风格)
  ↓
增强Prompt → LLM → 调整回复
  ↓
返回给用户
```

## 📊 返回数据结构

```python
{
    "detection": {
        "is_appropriate": bool,
        "violation_type": str,
        "detected_emotions": list,
        "detected_keywords": list,
        "suggestion": str
    },
    "affinity_change": {
        "original_change": int,
        "adjusted_change": int,
        "applied_rate": float,
        "protection_reason": str,
        "warnings": list
    },
    "affinity_state": {
        "before_score": int,
        "after_score": int,
        "before_level": str,
        "after_level": str,
        "level_changed": bool,
        "level_up": bool
    },
    "response_guidance": {
        "addressing_style": str,
        "formality": str,
        "intimacy_level": int,
        "emoji_usage": str,
        "suggested_tone": str,
        "suggested_response": str,
        "topic_suggestions": list
    },
    "trend": str,  # rising/falling/stable/volatile
    "recovery_suggestion": str
}
```

## 🧪 测试运行

```bash
# 运行测试套件
cd backend
python test_dynamic_response.py
```

测试包含8个场景:
1. 陌生阶段 - 礼貌问候
2. 陌生阶段 - 过于亲密(违规检测)
3. 朋友阶段 - 积极分享
4. 好友阶段 - 感谢与赞美
5. 特别的人 - 微妙情感
6. 心动阶段 - 表达思念
7. 恋人阶段 - 爱的表达
8. 负面情绪 - 生气抱怨

## 🎮 使用示例

### API调用示例

```bash
# 发送聊天消息
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "companion_id": 1,
    "message": "今天真开心！谢谢你一直陪着我！",
    "session_id": "test-session"
  }'
```

### Python代码示例

```python
from app.services.dynamic_response_system import dynamic_response_system

# 处理消息
result = dynamic_response_system.process_user_message(
    user_message="你好",
    current_affinity_score=100,
    user_id="user123",
    companion_id=1,
    current_mood="平静"
)

# 获取好感度变化
affinity_change = result["affinity_change"]["adjusted_change"]

# 获取回复指导
guidance = result["response_guidance"]

# 调整AI回复
adjusted = dynamic_response_system.generate_ai_response(
    "你好，很高兴见到你。",
    guidance
)
```

## 📈 好感度增长路径示例

```
初始 (50分, 陌生)
  ↓ 问候 +2分
52分 (陌生)
  ↓ 积极对话 +5分 × 10次
102分 (认识) ← 升级
  ↓ 分享故事 +8分 × 20次
262分 (朋友) ← 升级
  ↓ 深入交流 +10分 × 20次
462分 (好友) ← 升级
  ↓ 表达关心 +15分 × 15次
687分 (特别的人) ← 升级
  ↓ 浪漫互动 +20分 × 10次
887分 (心动) ← 升级
  ↓ 爱意表达 +30分 × 5次
1000分 (恋人) ← 升级
```

## ⚙️ 配置自定义

### 调整好感度规则

编辑 `app/services/content_detector.py`:

```python
AFFINITY_INCREASE_RULES = {
    "compliment": {
        "stranger": 2,      # 修改数值
        "friend": 5,
        # ...
    }
}
```

### 添加新的情感关键词

```python
EMOTION_KEYWORDS = {
    "positive": {
        "new_emotion": ["关键词1", "关键词2"]
    }
}
```

### 修改等级配置

编辑 `app/config/affinity_levels.py`:

```python
AFFINITY_LEVELS = {
    "custom_level": AffinityLevel(
        name="自定义等级",
        min_score=100,
        max_score=200,
        # ... 其他配置
    )
}
```

## 🔐 注意事项

1. **性能优化**: 系统使用内存缓存历史记录(最近20条)，生产环境建议使用Redis
2. **并发处理**: 保护器实例独立，多用户场景需要分别实例化
3. **等级变化通知**: 系统检测到等级变化时会记录日志，可以触发特殊事件
4. **容错机制**: 永远不会让好感度一次性暴涨或暴跌，保证体验平滑

## 📝 后续扩展建议

- [ ] 添加用户个性化配置 (调整敏感度)
- [ ] 支持多语言检测
- [ ] 引入情感强度评分
- [ ] 添加时间衰减机制 (长期不互动会降低好感度)
- [ ] 机器学习优化 (根据用户反馈自动调整规则)
- [ ] 添加特殊事件系统 (纪念日、生日等)

## 🆘 故障排查

### 好感度不更新
- 检查 Redis 连接
- 确认 `dynamic_response_system` 正确导入
- 查看日志 `chat_api` 的输出

### 回复风格不对
- 检查当前好感度分数和等级
- 确认 `response_guidance` 正确传递给 `generate_ai_response`
- 查看 `response_rules.py` 配置是否正确

### 等级跳变过快
- 检查保护机制是否启用
- 调整 `SINGLE_ADJUSTMENT_LIMITS` 的值
- 检查是否有异常的大量好感度增加

## 📄 许可与支持

集成到你的 AI-memory 项目中，遵循项目原有许可证。

---

**🎉 系统已完全集成并可立即使用！**

通过现有的 `/api/chat` 端点发送消息，系统会自动处理好感度、检测内容、调整回复风格。
