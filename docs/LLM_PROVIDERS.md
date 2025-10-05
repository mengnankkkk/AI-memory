# LLM服务提供商切换指南

## 📋 支持的提供商

### 1. Mock服务 (默认)
用于测试和演示，返回基于性格的模拟回复

```bash
LLM_PROVIDER=mock
```

### 2. 新Gradio API ⭐ (推荐)
基于 https://haiyangpengai-careyou.ms.show/

```bash
LLM_PROVIDER=new_gradio
NEW_GRADIO_API_URL=https://haiyangpengai-careyou.ms.show/
```

**特点**:
- ✅ 真实AI回复
- ✅ 支持TTS语音合成
- ✅ 可调节参数 (temperature, top_p, max_tokens)

### 3. DeepSeek Gradio
基于Hugging Face Space (需要网络访问)

```bash
LLM_PROVIDER=deepseek_gradio
DEEPSEEK_API_URL=Mengnankk/deepseek-ai-DeepSeek-V3.1-test
```

## 🔧 如何切换

### 方法1: 修改 `.env` 文件

```bash
# 编辑 backend/.env
LLM_PROVIDER=new_gradio  # 改为你想要的提供商
```

### 方法2: 环境变量

```bash
# Windows PowerShell
$env:LLM_PROVIDER="new_gradio"
python -m uvicorn app.main:app --reload

# Linux/Mac
export LLM_PROVIDER=new_gradio
python -m uvicorn app.main:app --reload
```

## 📊 提供商对比

| 提供商 | 真实AI | 速度 | 网络要求 | 成本 |
|--------|--------|------|----------|------|
| Mock | ❌ | ⚡⚡⚡ | ❌ | 免费 |
| New Gradio | ✅ | ⚡⚡ | ✅ | 免费 |
| DeepSeek Gradio | ✅ | ⚡ | ✅ (需翻墙) | 免费 |

## 🛠️ 自定义提供商

### Step 1: 创建服务类

在 `backend/app/services/llm/` 下创建新文件 `your_service.py`:

```python
from app.services.llm.base import BaseLLMService
from typing import List, Dict

class YourLLMService(BaseLLMService):
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        # 实现你的API调用逻辑
        pass

    def get_provider_name(self) -> str:
        return "Your Service Name"
```

### Step 2: 注册到工厂

编辑 `backend/app/services/llm/factory.py`:

```python
from app.services.llm.your_service import YourLLMService

# 在 create_service 方法中添加
elif provider == "your_service":
    return YourLLMService(api_url=settings.YOUR_API_URL)
```

### Step 3: 更新配置

在 `.env` 中添加:

```bash
LLM_PROVIDER=your_service
YOUR_API_URL=https://your-api-url.com
```

## 🔍 调试

### 查看当前提供商

启动后端时会打印:

```
✓ New Gradio API 客户端初始化成功
```

### 测试API调用

```bash
cd backend
python -c "
from app.services.llm.factory import llm_service
import asyncio

async def test():
    messages = [
        {'role': 'system', 'content': '你是一个温柔的助手'},
        {'role': 'user', 'content': '你好'}
    ]
    response = await llm_service.chat_completion(messages)
    print(response)

asyncio.run(test())
"
```

## ⚠️ 常见问题

### Q: 切换提供商后没有生效?

A: 需要重启后端服务:
```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
python -m uvicorn app.main:app --reload
```

### Q: New Gradio API调用失败?

A: 检查以下几点:
1. 网络连接是否正常
2. API URL是否正确
3. 查看后端日志获取详细错误

### Q: 如何回退到Mock模式?

A: 修改 `.env`:
```bash
LLM_PROVIDER=mock
```
