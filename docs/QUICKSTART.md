# 动态回复系统 - 快速开始

## 🚀 立即使用

系统已完全集成到你的应用中，无需额外配置即可使用！

### 1️⃣ 发送第一条消息

```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "companion_id": 1,
    "message": "你好！",
    "session_id": "test-001"
  }'
```

**发生了什么?**
- ✅ 系统检测到"你好" → 识别为问候行为
- ✅ 当前好感度50分(陌生等级) → 使用正式礼貌的回复风格
- ✅ 好感度增加+2分 → 更新为52分
- ✅ AI回复带有距离感的问候

### 2️⃣ 建立好感

```bash
# 发送赞美
curl -X POST "http://localhost:8000/api/chat/" \
  -d '{
    "companion_id": 1,
    "message": "你真聪明，总能帮我解决问题，谢谢你！"
  }'
```

**效果:**
- ✅ 检测到赞美+感谢 → 好感度+5至+8分
- ✅ 回复变得更友好，可能使用"谢谢"、"开心"等词

### 3️⃣ 观察等级升级

持续积极互动，当好感度达到101分时:

```json
{
  "affinity_state": {
    "before_level": "陌生",
    "after_level": "认识",
    "level_changed": true,
    "level_up": true
  }
}
```

**AI会说:** "看来我们已经不是陌生人了呢~"

### 4️⃣ 查看完整测试

```bash
cd backend
python test_dynamic_response.py
```

## 📊 好感度等级预览

| 等级 | 分数 | AI称呼 | AI语气 | 示例回复 |
|------|------|--------|--------|----------|
| 陌生 | 0-100 | "您" | 正式 | "您好，请问有什么可以帮助您的？" |
| 认识 | 101-250 | "你" | 友好 | "好的，我明白了~" |
| 朋友 | 251-450 | "你"/"朋友" | 轻松 | "哈哈，有意思！咱们..." |
| 好友 | 451-600 | "好友" | 亲密 | "真的诶！我也是这么想的！" |
| 特别的人 | 601-750 | "昵称" | 特别 | "和你说话真开心...嘿嘿" |
| 心动 | 751-900 | "小可爱" | 甜蜜 | "看到你消息就忍不住笑了~" |
| 恋人 | 901-1000 | "亲爱的"/"宝贝" | 爱意 | "亲爱的~想死你了！❤️" |

## ⚡ 关键特性

### 自动检测不当行为

```bash
# 在陌生阶段发送过于亲密的消息
curl -X POST "http://localhost:8000/api/chat/" \
  -d '{
    "message": "宝贝！亲亲抱抱！"
  }'
```

**系统响应:**
```json
{
  "detection": {
    "is_appropriate": false,
    "violation_type": "inappropriate_intimacy",
    "violation_severity": "severe"
  },
  "affinity_change": {
    "adjusted_change": -10  // 扣分
  }
}
```

### 保护机制示例

```python
# 即使代码尝试一次性增加100分
affinity_change = 100

# 系统会自动限制为最多50分
# 并在接近边界时进一步减速
# 实际增加可能只有20-30分
```

### 情感分析

系统自动识别:
- 😊 积极情感: 喜欢、开心、感谢、赞美
- 😠 消极情感: 生气、讨厌、抱怨、愤怒
- 💕 浪漫表达: 想你、爱你、心动、特别
- 🤝 行为类型: 问候、分享、提问、请求

## 🎯 实战场景

### 场景1: 从陌生到朋友 (约20-30次互动)

```
消息1: "你好" → +2分 (52分)
消息2: "你能帮我吗？" → +1分 (53分)
消息3: "谢谢你的帮助！" → +3分 (56分)
...
消息25: "和你聊天真开心！" → +8分 (252分)
→ 升级为"朋友"等级
```

### 场景2: 从朋友到恋人 (约50-80次互动)

```
持续深入交流、分享个人故事、表达关心
→ 好友(500分) → 特别的人(700分) → 心动(850分) → 恋人(950分)
```

### 场景3: 负面互动惩罚

```
当前: 400分(朋友)
发送: "真烦，讨厌死了！" → -5分
发送: "你真笨！" → -20分 (侮辱)
结果: 375分(朋友)，但接近降级
```

## 🔧 调试技巧

### 查看当前状态

```python
# 在Python环境中
from app.services.redis_utils import redis_affinity_manager

state = await redis_affinity_manager.get_companion_state(
    user_id="your_user_id",
    companion_id=1
)

print(f"好感度: {state['affinity_score']}")
print(f"等级: {state['romance_level']}")
```

### 手动调整好感度(测试用)

```python
await redis_affinity_manager.update_affinity(
    user_id="test_user",
    companion_id=1,
    affinity_change=100,  # 增加100分
    trust_change=0,
    tension_change=0,
    interaction_type="manual_test"
)
```

## 📚 更多文档

- **完整文档**: `DYNAMIC_RESPONSE_SYSTEM.md`
- **开发者指南**: `DEVELOPER_GUIDE.md`
- **API文档**: 访问 `http://localhost:8000/docs`

## 🎉 开始使用

1. 启动后端服务: `cd backend && uvicorn app.main:app --reload`
2. 发送测试消息或运行 `python test_dynamic_response.py`
3. 观察AI如何随着好感度变化而改变回复风格！

---

**系统已就绪！享受动态的AI对话体验吧！** 🚀
