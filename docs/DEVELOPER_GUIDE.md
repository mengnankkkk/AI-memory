# AI恋爱攻略系统开发者指南

## 快速开始

### 系统要求
- Python 3.8+
- Node.js 16+
- Redis 6.0+
- Git

### 一键启动
```bash
# Linux/Mac
chmod +x start_romance_system.sh
./start_romance_system.sh

# Windows
start_romance_system.bat
```

## 项目结构概览

```
AI-memory/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/
│   │   │   ├── romance.py     # 恋爱攻略 API ✨
│   │   │   ├── chat.py        # 聊天 API (已升级) ⭐
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── redis_utils.py # Redis 工具类 (已扩展) ⭐
│   │   │   └── ...
│   │   └── schemas_romance.py  # 恋爱攻略数据模型 ✨
│   └── requirements.txt
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/
│   │   │   └── RomancePanel.vue # 恋爱攻略面板 ✨
│   │   ├── services/
│   │   │   └── romance.ts      # 恋爱攻略 API 服务 ✨
│   │   ├── types/
│   │   │   └── romance.ts      # TypeScript 类型定义 ✨
│   │   └── views/
│   │       └── Chat.vue        # 聊天页面 (已升级) ⭐
│   └── package.json
├── AI恋爱攻略实施方案.md        # 详细实施方案 ✨
├── start_romance_system.sh      # Linux/Mac 启动脚本 ✨
└── start_romance_system.bat     # Windows 启动脚本 ✨

✨ = 新增文件
⭐ = 重要修改
```

## 核心功能说明

### 1. 好感度系统 (`RedisAffinityManager`)

**位置**: `backend/app/services/redis_utils.py`

**核心功能**:
- 好感度计算和更新
- 关系阶段自动升级 (初识 → 朋友 → 恋人 → 深爱)
- AI心情状态管理
- 记忆系统

**使用示例**:
```python
from app.services.redis_utils import redis_affinity_manager

# 更新好感度
await redis_affinity_manager.update_affinity(
    user_id="user123",
    companion_id=1,
    affinity_change=5,
    trust_change=1,
    interaction_type="compliment"
)

# 获取伙伴状态
state = await redis_affinity_manager.get_companion_state("user123", 1)
```

### 2. 恋爱攻略 API (`/api/romance/`)

**位置**: `backend/app/api/romance.py`

**主要端点**:
- `GET /companion/{id}/state` - 获取关系状态
- `POST /companion/{id}/gift` - 赠送礼物
- `POST /companion/{id}/random-event` - 触发随机事件
- `GET /companion/{id}/daily-tasks` - 获取每日任务

### 3. 前端恋爱攻略面板

**位置**: `frontend/src/components/RomancePanel.vue`

**功能**:
- 实时显示好感度和关系阶段
- 礼物赠送界面
- 每日任务列表
- 特殊事件提醒
- 珍贵回忆展示

## 开发指南

### 添加新的礼物类型

1. **后端**: 在 `romance.py` 的 `_generate_gift_reaction` 函数中添加新礼物反应
2. **前端**: 在 `types/romance.ts` 的 `GIFT_CONFIGS` 中添加配置

```typescript
// frontend/src/types/romance.ts
export const GIFT_CONFIGS = {
  'new_gift_type': { emoji: '🎁', affinity: 20 }
}
```

### 添加新的关系阶段

1. **后端**: 修改 `RedisAffinityManager._calculate_romance_level` 方法
2. **前端**: 更新 `types/romance.ts` 的 `ROMANCE_LEVELS` 数组

### 添加新的随机事件

在 `RedisEventManager._get_available_events` 方法中添加新事件:

```python
new_events = [
    {
        "type": "new_event_type",
        "title": "新事件标题",
        "description": "事件描述",
        "affinity_requirement": 300
    }
]
```

### 自定义AI回复逻辑

修改 `chat.py` 中的 `_build_romance_enhanced_prompt` 函数来调整AI根据恋爱状态的回复风格。

## 数据库迁移

如果您需要添加新的数据库字段，请创建相应的迁移脚本：

```python
# 示例：添加新字段到 companions 表
ALTER TABLE companions ADD COLUMN romance_style VARCHAR(50) DEFAULT 'normal';
```

## Redis 数据结构

### 伙伴状态
```
Key: companion_state:{user_id}:{companion_id}
Type: String (JSON)
TTL: 30 days

Data Structure:
{
  "affinity_score": 350,
  "trust_score": 45,
  "tension_score": 5,
  "romance_level": "特别的人",
  "current_mood": "开心",
  "memories": [...],
  "gifts_received": [...]
}
```

### 事件队列
```
Key: event_queue:{user_id}:{companion_id}
Type: List
TTL: 24 hours
```

## 性能优化建议

1. **Redis 连接池**: 确保 Redis 连接池配置合理
2. **数据缓存**: 热点数据使用 Redis 缓存
3. **异步处理**: 使用异步函数处理 I/O 密集型操作
4. **批量操作**: 对于大量数据操作，使用 Redis 管道

## 监控和调试

### 后端日志
```python
import logging
logger = logging.getLogger("romance_system")
logger.info("好感度更新: user123 -> companion1, +5")
```

### 前端调试
使用浏览器开发者工具监控 API 调用：
```javascript
// 在 romance.ts 中添加调试日志
console.log('Romance API call:', endpoint, data)
```

### Redis 监控
```bash
# 监控 Redis 命令
redis-cli monitor

# 查看特定键
redis-cli get "companion_state:user123:1"
```

## 测试指南

### 后端 API 测试
```bash
# 获取伙伴状态
curl "http://localhost:8000/api/romance/companion/1/state?user_id=test"

# 赠送礼物
curl -X POST "http://localhost:8000/api/romance/companion/1/gift" \
  -H "Content-Type: application/json" \
  -d '{"companion_id":1,"gift_type":"flower","gift_name":"红玫瑰","user_id":"test"}'
```

### 前端组件测试
```vue
<!-- 在开发环境中测试恋爱攻略面板 -->
<RomancePanel
  :companion-id="1"
  :companion-name="测试伙伴"
  :user-id="test-user"
/>
```

## 部署注意事项

### 生产环境配置
1. **Redis 持久化**: 启用 RDB 和 AOF
2. **数据库备份**: 定期备份用户数据
3. **负载均衡**: 配置多个后端实例
4. **CDN**: 静态资源使用 CDN

### 环境变量
```bash
# .env 文件
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite:///./app.db
LLM_PROVIDER=deepseek
```

## 常见问题

### Q: 好感度不更新？
A: 检查 Redis 连接和 `redis_affinity_manager` 是否正确调用

### Q: 前端组件不显示数据？
A: 确认 API 端点正确，检查浏览器网络面板的错误信息

### Q: 随机事件不触发？
A: 检查好感度是否达到事件要求，调整事件触发概率

## 路线图

### 近期计划 (1-2 周)
- [ ] 完善商店系统
- [ ] 添加成就系统  
- [ ] 优化AI回复质量

### 中期计划 (1-2 月)
- [ ] 多语言支持
- [ ] 语音交互
- [ ] 社交功能

### 长期计划 (3-6 月)
- [ ] AR/VR 体验
- [ ] 自定义角色创建
- [ ] 多模态交互

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/new-feature`)
3. 提交更改 (`git commit -am 'Add new feature'`)
4. 推送到分支 (`git push origin feature/new-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

---

**联系方式**: 如有问题，请创建 GitHub Issue 或联系开发团队。

🎉 **享受构建 AI恋爱攻略系统的乐趣吧！**
