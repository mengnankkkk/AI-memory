# AI灵魂伙伴 (Project Listener) 💖

> 多模型支持的AI虚拟伴侣系统 - 让每一次对话都充满温暖与理解

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.4-4FC08D?logo=vue.js)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)

## 🎯 项目简介

一个轻量级AI虚拟伴侣MVP,专注于打造高质量的情感对话体验。用户可以创建拥有独特性格的AI伙伴,随时进行温暖、真诚的交流。

### ✨ 核心特性

- 🎭 **3种性格原型**: 温柔倾听者 | 元气鼓励者 | 理性分析者
- 💬 **实时对话**: 流畅的即时通讯体验
- 🧠 **会话记忆**: 智能上下文管理
- 🎨 **精美UI**: 基于TailwindCSS的现代化界面
- 🚀 **快速部署**: 简单易用的开发环境

## 🏗️ 技术架构

```
┌─────────────────────────────────┐
│      Vue 3 + TypeScript         │  前端
│      TailwindCSS + Vite         │
└───────────┬─────────────────────┘
            │ HTTP/Axios
┌───────────▼─────────────────────┐
│         FastAPI                 │  后端
│    + SQLAlchemy (SQLite)        │
└───────────┬─────────────────────┘
            │
┌───────────▼─────────────────────┐
│      🤖 多LLM支持                │  LLM
│   ✨ Google Gemini 2.0 Flash     │  (推荐)
│   🔷 DeepSeek V3.1 (Gradio)     │
│   🎭 Mock模式                    │
└─────────────────────────────────┘
```

### 🎯 支持的LLM提供商

| 提供商 | 模型 | 特点 | 推荐场景 |
|--------|------|------|----------|
| **Gemini** ✨ | gemini-2.0-flash-exp | 最新、最强、响应快 | **生产环境推荐** |
| DeepSeek | DeepSeek V3.1 | 开源、Gradio接入 | 备选方案 |
| Mock | 本地模拟 | 快速测试 | 开发调试 |

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+

### 启动步骤

**1. 后端启动**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# 🔑 配置API Key (选择一个)
# 选项1: 使用Gemini (推荐) - 访问 https://ai.google.dev/ 获取API Key
# 编辑 .env 文件:
# LLM_PROVIDER=gemini
# GEMINI_API_KEY=你的API密钥

# 选项2: 使用DeepSeek/Mock
# (保持默认配置即可)

python -m uvicorn app.main:app --reload
```

**2. 前端启动** (新终端)
```bash
cd frontend
npm install
npm run dev
```

**3. 访问应用**

打开浏览器访问 `http://localhost:5173`

📖 **完整教程**: [QUICKSTART.md](docs/QUICKSTART.md)

## 🎭 性格原型

### 💖 温柔的倾听者
- **适合**: 倾诉烦恼、寻求安慰
- **特质**: 同理心强、语言温暖

### ✨ 元气的鼓励者
- **适合**: 需要打气、分享喜悦
- **特质**: 积极向上、充满活力

### 🧠 理性的分析者
- **适合**: 解决问题、理性分析
- **特质**: 逻辑清晰、结构化思考

## 📚 文档

- [快速开始](docs/QUICKSTART.md) - 详细安装教程
- [Gemini配置](docs/GEMINI_SETUP.md) - Google Gemini API配置指南 ✨
- [DeepSeek配置](docs/DEEPSEEK_SETUP.md) - DeepSeek模型部署指南
- [技术设计](AI灵魂伙伴-技术实施计划书.md) - 完整技术方案

## 📈 开发路线

### ✅ Phase 1: MVP (已完成)
- 基础架构
- 3种性格原型
- 实时对话
- 精美UI

### 🔄 Phase 2: 增强 (计划中)
- Redis持久化
- 流式输出
- 语音对话
- VRM虚拟形象

### 🌟 Phase 3: 高级 (未来)
- 长期记忆(RAG)
- 多伙伴管理
- 主动交互
- 移动端PWA

## 🤝 参考项目

- [TEN Framework](https://github.com/TEN-framework/ten-framework)
- [AIRI](https://github.com/moeru-ai/airi)

## 📄 License

MIT

---

**Made with 💖**
