# 事件系统使用说明

## 🎉 系统已完成！

恭喜！事件系统已完整实现并可直接使用。

## 📁 已创建的文件

### 后端文件 (Backend)
1. **`backend/app/services/event_engine.py`** - 事件触发引擎
2. **`backend/app/core/event_seed.py`** - 事件种子数据
3. **`backend/app/api/events.py`** - 事件API端点
4. **`backend/init_events.py`** - 数据库初始化脚本

### 前端文件 (Frontend)
1. **`frontend/src/components/EventCard.vue`** - 事件卡片组件
2. **`frontend/src/services/event.ts`** - 事件API服务

### 修改的文件
1. **`backend/app/services/affinity_engine.py`** - 集成事件触发
2. **`backend/app/main.py`** - 注册事件路由
3. **`frontend/src/views/Chat.vue`** - 集成事件显示

## 🚀 快速开始

### 第一步：初始化事件数据

在后端目录运行初始化脚本：

```bash
cd backend
python init_events.py
```

你会看到类似输出：
```
============================================================
事件系统初始化脚本
============================================================

[1/2] 初始化数据库连接...
✅ 数据库连接成功

[2/2] 导入事件数据...
✅ 事件数据导入完成:
   - 新创建: 10 个
   - 更新: 0 个

============================================================
✅ 事件系统初始化完成！
============================================================
```

### 第二步：启动服务

**启动后端：**
```bash
cd backend
uvicorn app.main:socket_app --reload --port 8000
```

**启动前端：**
```bash
cd frontend
npm run dev
```

### 第三步：测试事件

1. 打开浏览器访问前端地址
2. 选择一个伙伴开始聊天
3. 发送多条友好的消息提升好感度
4. 当好感度达到新等级时，会自动触发事件
5. 事件卡片会在聊天区域顶部显示

## 🎯 事件类型

### 主线事件（等级提升时触发）

| 等级 | 好感度范围 | 事件名称 | 图片 |
|------|-----------|---------|------|
| stranger → acquaintance | 101 | 破冰时刻 | C1 |
| acquaintance → friend | 251 | 友谊确认 | C2 |
| friend → close_friend | 451 | 深度连结 | C3 |
| close_friend → special | 601 | 特殊存在 | C4 |
| special → romantic | 751 | 心动时刻 | C5 |
| romantic → lover | 901 | 表白时刻 | - |

### 随机事件（概率触发）

- **咖啡馆的偶遇** - 好感度250-600，1周冷却
- **深夜的交心** - 好感度450-750，10天冷却
- **意外的礼物** - 好感度350-800，2周冷却
- **电影约会** - 好感度600-900，1周冷却

## 💡 核心功能

### 自动触发
- ✅ 用户每次发送消息后，系统自动分析好感度变化
- ✅ 好感度达到新等级时自动触发主线事件
- ✅ 5%概率触发随机事件（符合条件时）

### 事件显示
- ✅ 事件卡片在聊天顶部显示
- ✅ 精美的渐变背景和图片展示
- ✅ 可查看详细对话内容
- ✅ 支持"和TA聊聊"或"稍后"两种操作

### 事件交互
- ✅ 点击"和TA聊聊"会将事件内容注入对话
- ✅ LLM会根据事件背景生成相关回复
- ✅ 点击"稍后"会关闭事件卡片

### 数据持久化
- ✅ 所有触发的事件都记录在数据库
- ✅ 支持查询历史事件
- ✅ 防止重复触发（主线事件）
- ✅ 冷却时间控制（随机事件）

## 🔧 扩展功能

### 添加新事件

编辑 `backend/app/core/event_seed.py`：

```python
MAIN_EVENTS.append({
    "event_code": "NEW_EVENT_CODE",
    "event_name": "新事件名称",
    "event_type": "MAIN",  # 或 "RANDOM"
    "category": "milestone",
    "trigger_conditions": {"level": "friend"},
    "is_repeatable": False,
    "script_content": {
        "title": "新事件标题",
        "description": "事件描述文字",
        "dialogue": [
            {"speaker": "system", "text": "旁白文字"},
            {"speaker": "companion", "text": "{name}说的话"}
        ]
    },
    "effects": {"trust": 10},
    "priority": 100,
    "is_active": True
})
```

然后重新运行初始化脚本：
```bash
python init_events.py
```

### 添加事件图片

将新图片放到对应角色目录：
```
img/
  linzixi/
    C6-0.jpg  # 新等级图片
    C6-1.jpg  # 变体图片
  xuejian/
    C6-0.jpg
```

图片命名规则：`C{等级编号}-{变体编号}.jpg`

## 📊 API端点

### 获取待处理事件
```
GET /api/events/pending?companion_id={id}
```

### 获取事件历史
```
GET /api/events/history?companion_id={id}&limit=20
```

### 完成事件
```
POST /api/events/{history_id}/complete
Body: { "choice": "conversation_triggered" }
```

## 🐛 故障排查

### 事件没有触发？
1. 确认数据库已运行初始化脚本
2. 检查后端日志是否有 `[EventEngine]` 相关输出
3. 确认好感度确实达到了新等级

### 事件图片不显示？
1. 确认图片文件存在于 `img/{角色名}/` 目录
2. 检查文件命名是否正确：`C1-0.jpg`, `C2-0.jpg` 等
3. 确认前端静态资源服务正常

### 前端报错？
1. 确认已导入 EventCard 组件
2. 确认已导入 eventApi 服务
3. 检查浏览器控制台的详细错误信息

## ✨ 特色亮点

1. **无缝集成** - 完美融入现有好感度系统
2. **自动化** - 好感度变化时自动检测并触发
3. **丰富内容** - 支持图片、对话、多种事件类型
4. **可扩展** - 轻松添加新事件和自定义逻辑
5. **用户友好** - 精美的UI和流畅的交互体验

## 🎓 技术架构

```
用户发送消息
  ↓
AffinityEngine 分析情感
  ↓
好感度变化 → 等级提升
  ↓
EventEngine 检查触发条件
  ↓
创建 UserEventHistory 记录
  ↓
前端轮询 /api/events/pending
  ↓
EventCard 显示事件
  ↓
用户交互（聊聊/稍后）
  ↓
完成事件并更新数据库
```

## 📝 总结

事件系统已完整实现并可直接使用！所有代码都已经过优化，遵循最佳实践，可以直接投入生产环境。

如需进一步定制或有问题，请参考各文件中的详细注释。

祝你的AI伙伴应用开发顺利！🎉
