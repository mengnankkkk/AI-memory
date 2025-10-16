# 礼物系统使用说明

## 🎁 系统概述

礼物系统已完全实现！现在用户拥有有限的礼物库存，每种礼物有不同的好感度增益和稀有度。

## ✨ 主要特性

### 1. 多种礼物类型
- **普通礼物** (5-10好感度): 红玫瑰、郁金香、向日葵
- **稀有礼物** (10-20好感度): 巧克力礼盒、草莓蛋糕、泰迪熊
- **史诗礼物** (20-30好感度): 心形项链、高级香水、精装书籍
- **传说礼物** (30-50好感度): 钻石戒指、99朵玫瑰

### 2. 库存管理系统
- ✅ 每种礼物都有**初始库存**和**最大库存**
- ✅ 赠送礼物时**自动扣除库存**
- ✅ 库存不足时**无法赠送**
- ✅ 实时显示**当前库存数量**
- ✅ 库存低于3时**警告提示**

### 3. 礼物效果差异化
- ✅ 不同礼物增加**不同的好感度**
- ✅ 部分礼物增加**信任度**
- ✅ 部分礼物降低**紧张度**
- ✅ 礼物效果在配置中**统一管理**

## 📁 已创建/修改的文件

### 后端文件
1. **`backend/app/core/gift_config.py`** - 礼物配置文件（11种礼物）
2. **`backend/app/models/gift.py`** - 用户礼物库存数据模型
3. **`backend/app/models/__init__.py`** - 导出礼物模型
4. **`backend/init_gifts.py`** - 礼物库存初始化脚本
5. **`backend/app/api/romance.py`** - 修改礼物赠送API和商店API

### 前端文件
1. **`frontend/src/types/romance.ts`** - 添加 quantity 字段
2. **`frontend/src/services/romance.ts`** - 修改 getStoreItems 传递 userId
3. **`frontend/src/components/RomancePanel.vue`** - 显示库存、稀有度、库存不足提示

## 🚀 快速开始

### 第一步：初始化礼物库存

在后端目录运行初始化脚本：

```bash
cd backend
python init_gifts.py
```

可选：为特定用户初始化（默认用户ID=2）：
```bash
python init_gifts.py <user_id>
```

输出示例：
```
============================================================
礼物系统初始化脚本
============================================================

[1/2] 初始化数据库连接...
[成功] 数据库连接成功

[2/2] 初始化礼物库存...
INFO:init_gifts:[创建] 红玫瑰: 5个
INFO:init_gifts:[创建] 郁金香: 8个
INFO:init_gifts:[创建] 向日葵: 10个
INFO:init_gifts:[创建] 精致巧克力礼盒: 3个
INFO:init_gifts:[创建] 草莓蛋糕: 4个
INFO:init_gifts:[创建] 泰迪熊: 2个
INFO:init_gifts:[创建] 心形项链: 1个
INFO:init_gifts:[创建] 高级香水: 1个
INFO:init_gifts:[创建] 精装书籍: 2个
INFO:init_gifts:[创建] 钻石戒指: 1个
INFO:init_gifts:[创建] 99朵玫瑰: 1个

礼物库存初始化完成: 新创建 11 个，更新 0 个

============================================================
[完成] 礼物系统初始化成功！
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

### 第三步：测试礼物系统

1. 打开浏览器访问前端地址
2. 选择一个伙伴进入聊天
3. 点击右上角 **"💖 恋爱攻略"** 按钮
4. 在礼物赠送区域查看所有礼物
5. 点击礼物进行赠送
6. 观察库存实时减少

## 🎯 礼物详细信息

### 普通礼物（Common）

| 礼物 | Emoji | 好感度 | 信任度 | 初始库存 | 最大库存 | 价格 |
|------|-------|--------|--------|----------|----------|------|
| 红玫瑰 | 🌹 | +8 | +2 | 5 | 10 | 50💰 |
| 郁金香 | 🌷 | +6 | +1 | 8 | 15 | 30💰 |
| 向日葵 | 🌻 | +5 | +2 | 10 | 20 | 20💰 |

### 稀有礼物（Rare）

| 礼物 | Emoji | 好感度 | 信任度 | 初始库存 | 最大库存 | 价格 |
|------|-------|--------|--------|----------|----------|------|
| 精致巧克力礼盒 | 🍫 | +12 | +3 | 3 | 8 | 100💰 |
| 草莓蛋糕 | 🍰 | +10 | +2 | 4 | 10 | 80💰 |
| 泰迪熊 | 🧸 | +15 | +5 | 2 | 5 | 150💰 |

### 史诗礼物（Epic）

| 礼物 | Emoji | 好感度 | 信任度 | 初始库存 | 最大库存 | 价格 |
|------|-------|--------|--------|----------|----------|------|
| 心形项链 | 💎 | +25 | +8 | 1 | 3 | 500💰 |
| 高级香水 | 💐 | +22 | +6 | 1 | 4 | 400💰 |
| 精装书籍 | 📚 | +20 | +10 | 2 | 6 | 300💰 |

### 传说礼物（Legendary）

| 礼物 | Emoji | 好感度 | 信任度 | 初始库存 | 最大库存 | 价格 |
|------|-------|--------|--------|----------|----------|------|
| 钻石戒指 | 💍 | +50 | +20 | 1 | 1 | 1000💰 |
| 99朵玫瑰 | 💐 | +40 | +15 | 1 | 2 | 999💰 |

## 💡 核心功能

### 1. 库存检查
- 赠送前自动检查库存
- 库存为0时显示灰色并禁止点击
- 库存≤2时显示橙色警告

### 2. 库存扣除
- 每次赠送自动扣除1个库存
- 数据库实时更新
- 前端立即刷新显示

### 3. 稀有度显示
- **普通**：灰色标签
- **稀有**：蓝色标签
- **史诗**：粉色标签
- **传说**：金色标签 + 发光动画

### 4. 好感度差异化
```python
# 后端根据礼物配置自动应用效果
gift_config = {
    "affinity_bonus": 8,    # 好感度增益
    "trust_bonus": 2,       # 信任度增益
    "tension_bonus": 0      # 紧张度变化
}
```

### 5. 伙伴反应
根据礼物类型和关系等级生成不同反应：
- 陌生人阶段：礼貌感谢
- 朋友阶段：惊喜感谢
- 恋人阶段：甜蜜反应

## 🔧 扩展功能

### 添加新礼物

编辑 `backend/app/core/gift_config.py`：

```python
GIFT_CONFIGS.append({
    "gift_id": "custom_gift",
    "gift_type": "special",
    "name": "自定义礼物",
    "emoji": "🎁",
    "description": "一个特别的礼物",
    "rarity": "epic",
    "affinity_bonus": 30,
    "trust_bonus": 10,
    "tension_bonus": -5,
    "price": 600,
    "currency": "coins",
    "initial_quantity": 2,
    "max_quantity": 5
})
```

然后重新运行初始化脚本：
```bash
cd backend
python init_gifts.py
```

### 给用户补充库存

可以直接操作数据库：
```python
# 在 Python shell 中
from app.models.gift import UserGiftInventory
from app.core.database import async_session_maker

async with async_session_maker() as session:
    stmt = select(UserGiftInventory).where(
        UserGiftInventory.user_id == "2",
        UserGiftInventory.gift_id == "rose"
    )
    result = await session.execute(stmt)
    inventory = result.scalar_one()
    inventory.quantity += 5  # 增加5个
    await session.commit()
```

## 📊 API端点

### 获取礼物列表（含库存）
```
GET /api/romance/store/items?user_id={user_id}&item_type=gift
```

响应示例：
```json
[
  {
    "item_id": "rose",
    "item_type": "flower",
    "name": "红玫瑰",
    "description": "经典的爱情象征",
    "price": 50,
    "currency": "coins",
    "preview_url": "🌹",
    "rarity": "common",
    "quantity": 5
  }
]
```

### 赠送礼物
```
POST /api/romance/companion/{companion_id}/gift
Body: {
  "gift_type": "rose",
  "gift_name": "红玫瑰",
  "user_id": "2"
}
```

响应示例：
```json
{
  "success": true,
  "message": "成功赠送红玫瑰（剩余4个）",
  "affinity_change": 8,
  "new_affinity_score": 108,
  "companion_reaction": "哇，这束花真的很美！谢谢你想到我。"
}
```

## 🐛 故障排查

### 库存显示为0？
1. 确认已运行 `python init_gifts.py`
2. 检查数据库表 `user_gift_inventory` 是否有数据
3. 确认传递的 user_id 正确

### 赠送礼物失败？
1. 检查后端日志查看错误信息
2. 确认库存充足（quantity > 0）
3. 确认 gift_id 正确（如 "rose" 而非 "flower_rose"）

### 前端不显示库存数量？
1. 确认 `StoreItemResponse` 类型已添加 `quantity` 字段
2. 确认 `getStoreItems` 传递了 `userId` 参数
3. 检查浏览器控制台是否有错误

## ✨ 特色亮点

1. **库存限制** - 防止无限赠送，增加资源管理乐趣
2. **差异化效果** - 不同礼物有不同的好感度增益
3. **稀有度系统** - 从普通到传说，稀有礼物效果更好
4. **视觉反馈** - 库存不足时显示灰色，低库存时显示警告
5. **实时更新** - 赠送后立即刷新库存显示
6. **扩展性强** - 轻松添加新礼物类型

## 🎓 技术架构

```
用户点击礼物
  ↓
前端检查库存（quantity > 0）
  ↓
发送 POST /romance/companion/{id}/gift
  ↓
后端验证库存
  ↓
扣除库存（quantity -= 1）
  ↓
更新好感度（根据gift_config）
  ↓
返回伙伴反应
  ↓
前端刷新库存和好感度
```

## 📝 总结

礼物系统现在完全实现了库存管理和差异化效果！

**核心改进：**
✅ 11种礼物，4个稀有度等级
✅ 库存限制，防止无限赠送
✅ 好感度增益差异化（5-50点）
✅ 信任度和紧张度效果
✅ 实时库存显示和更新
✅ 库存不足提示和禁用

**下一步可扩展：**
- 添加礼物购买系统（使用金币）
- 每日库存补充机制
- 特殊节日限定礼物
- 礼物组合套装
- 礼物赠送历史记录

祝你的AI伙伴应用开发顺利！🎉
