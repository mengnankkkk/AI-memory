# 礼物系统前端显示问题调试指南

## 当前状态
- ✅ 后端API正常（返回11个礼物）
- ✅ 数据库表存在且有数据
- ✅ RomancePanel组件已集成到Chat.vue
- ❓ 前端显示待验证

## 调试步骤

### 1. 启动前端应用
```bash
cd E:\github\AI-memory\frontend
npm run dev
```

### 2. 打开聊天页面
1. 访问 http://localhost:5173
2. 进入任意伙伴的聊天页面
3. 点击右上角的 "💖 恋爱攻略" 按钮（粉色按钮）

### 3. 打开浏览器开发者工具
- 按 F12 打开开发者工具
- 切换到 "Console"（控制台）标签

### 4. 查看控制台输出
应该看到以下调试信息：
```
[RomancePanel] 组件挂载, props: {companionId: ..., companionName: ..., userId: ...}
[RomancePanel] 开始加载礼物列表, userId: 2
[RomancePanel] 礼物列表加载成功: 11 个礼物
[RomancePanel] 礼物详情: [Array(11)]
[RomancePanel] 所有数据加载完成, availableGifts: 11 个
```

### 5. 检查网络请求
- 切换到 "Network"（网络）标签
- 筛选 "Fetch/XHR"
- 查找 `/romance/store/items` 请求
- 检查：
  - 请求状态码是否为 200
  - 请求参数是否包含 `user_id=2` 和 `item_type=gift`
  - 响应数据是否包含 11 个礼物对象

## 可能的问题和解决方案

### 问题1: "💖 恋爱攻略" 按钮不显示
**原因**: 按钮可能被其他元素遮挡或CSS问题
**解决**: 检查浏览器控制台是否有CSS错误

### 问题2: 点击按钮后侧边栏不显示
**原因**: `showRomancePanel` 状态没有正确切换
**解决**:
1. 在控制台中检查是否有Vue警告
2. 确认Chat.vue中的按钮点击事件正常

### 问题3: 侧边栏显示但没有礼物
**原因1**: API调用失败
- 检查控制台是否有错误信息 `[RomancePanel] 加载礼物列表失败`
- 检查Network标签中的API请求是否失败

**原因2**: 数据格式问题
- 展开礼物详情数组，检查每个礼物对象
- 确认每个对象都有：`item_id, name, quantity, emoji, rarity`

**原因3**: userId不正确
- 检查控制台输出的userId是否为 "2"
- 如果不是，需要确认用户登录状态

### 问题4: 礼物显示但没有图标
**原因**: `emoji` 字段为空或不存在
**解决**: 检查礼物详情数组中每个对象的emoji字段

## 额外检查

### 手动测试API
在浏览器控制台中执行：
```javascript
fetch('http://localhost:8000/romance/store/items?user_id=2&item_type=gift')
  .then(r => r.json())
  .then(d => console.log('API返回:', d))
```

应该看到包含11个礼物的数组。

### 检查前端服务配置
确认 `frontend/src/services/auth.ts` 中API baseURL配置正确：
```typescript
baseURL: 'http://localhost:8000'
```

## 下一步
根据控制台输出结果，提供具体的错误信息以便进一步诊断。
