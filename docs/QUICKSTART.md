# 快速开始指南

## 环境要求

- Python 3.11+
- Node.js 18+
- npm 或 pnpm

## 安装步骤

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd AI-memory
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量配置
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
```

### 3. 前端设置

```bash
cd ../frontend

# 安装依赖
npm install
# 或使用 pnpm
# pnpm install
```

## 启动应用

### 启动后端

```bash
cd backend
python -m uvicorn app.main:app --reload
```

后端将运行在: `http://localhost:8000`

API文档: `http://localhost:8000/docs`

### 启动前端

新开一个终端窗口:

```bash
cd frontend
npm run dev
```

前端将运行在: `http://localhost:5173`

## 使用流程

1. 打开浏览器访问 `http://localhost:5173`
2. 点击"创建我的AI伙伴"按钮
3. 按照3步流程创建你的伙伴:
   - Step 1: 给TA起名字
   - Step 2: 选择形象
   - Step 3: 选择性格原型
4. 开始对话!

## 性格原型说明

### 💖 温柔的倾听者
- **适合场景**: 倾诉烦恼、寻求安慰
- **语言风格**: 温暖、治愈、同理心强
- **典型用语**: "我理解"、"听起来"、"你一定"

### ✨ 元气的鼓励者
- **适合场景**: 需要打气、分享喜悦
- **语言风格**: 积极、活力、正能量
- **典型用语**: "太棒了"、"你真厉害"、"继续加油"

### 🧠 理性的分析者
- **适合场景**: 解决问题、理性分析
- **语言风格**: 逻辑清晰、客观理性
- **典型用语**: "首先...其次"、"从几个维度分析"

## 常见问题

### Q: DeepSeek API调用失败怎么办?

A: 检查以下几点:
1. 网络连接是否正常
2. Hugging Face Space是否在线
3. 查看后端日志获取详细错误信息

### Q: 前端无法连接后端?

A: 确保:
1. 后端已启动并运行在8000端口
2. 检查前端 `vite.config.ts` 中的proxy配置
3. 清除浏览器缓存重试

### Q: 对话回复很慢?

A: 这是正常现象,DeepSeek模型推理需要时间,通常3-10秒。

## 项目结构

```
AI-memory/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── companions.py  # 伙伴管理
│   │   │   └── chat.py        # 聊天接口
│   │   ├── core/           # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── database.py    # 数据库
│   │   │   └── prompts.py     # 性格模板
│   │   ├── models/         # 数据模型
│   │   │   └── companion.py
│   │   ├── services/       # 业务逻辑
│   │   │   └── deepseek.py    # DeepSeek集成
│   │   └── main.py         # 应用入口
│   └── requirements.txt
├── frontend/               # Vue 3前端
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── views/         # 页面
│   │   │   ├── Home.vue          # 首页
│   │   │   ├── CreateCompanion.vue  # 创建流程
│   │   │   └── Chat.vue          # 聊天界面
│   │   ├── services/      # API服务
│   │   ├── types/         # 类型定义
│   │   └── router/        # 路由配置
│   └── package.json
└── docs/                   # 文档
```

## 下一步优化方向

- [ ] 集成Redis实现持久化会话存储
- [ ] 实现流式输出(Server-Sent Events)
- [ ] 添加用户认证系统
- [ ] 支持多伙伴管理
- [ ] 添加语音对话功能
- [ ] 集成VRM虚拟形象
- [ ] 实现长期记忆系统

## 技术支持

遇到问题?

1. 查看后端日志: 在后端终端查看详细错误
2. 查看浏览器控制台: F12打开开发者工具
3. 提交Issue: 在GitHub上创建Issue

---

**Happy Coding! 💖**
