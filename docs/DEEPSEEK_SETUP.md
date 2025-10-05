# 部署DeepSeek API适配器

由于你使用的是Hugging Face Gradio Space上的DeepSeek模型,需要确认API调用方式。

## 方法一: 直接使用Gradio Client (推荐)

当前代码已实现,无需修改。

**优点**: 简单直接
**缺点**: 可能受Hugging Face Space限制

## 方法二: 部署本地DeepSeek

如果Hugging Face不稳定,可以考虑本地部署:

### 使用Ollama

```bash
# 安装Ollama
# 访问 https://ollama.com/download

# 拉取DeepSeek模型
ollama pull deepseek-coder

# 启动服务(默认11434端口)
ollama serve
```

### 修改后端配置

```python
# backend/app/services/deepseek.py

from openai import AsyncOpenAI

class DeepSeekService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"  # Ollama不需要真实key
        )

    async def chat_completion(self, messages, stream=False):
        response = await self.client.chat.completions.create(
            model="deepseek-coder",
            messages=messages,
            stream=stream
        )
        return response.choices[0].message.content
```

## 方法三: 使用OpenAI兼容API

支持任何OpenAI兼容的API(如DeepSeek官方API):

```python
# .env文件
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# services/deepseek.py
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_BASE_URL
)
```

## 调试DeepSeek集成

### 测试Gradio API

```python
# test_deepseek.py
from gradio_client import Client

client = Client("Mengnankk/deepseek-ai-DeepSeek-V3.1-test")

# 查看可用的API endpoints
print(client.view_api())

# 测试调用
result = client.predict(
    "你好,请介绍一下自己",
    api_name="/chat"  # 根据实际endpoint调整
)
print(result)
```

运行测试:

```bash
cd backend
python test_deepseek.py
```

### 常见问题

**1. API endpoint错误**

检查Hugging Face Space的实际API:
- 访问: https://huggingface.co/spaces/Mengnankk/deepseek-ai-DeepSeek-V3.1-test
- 查看API文档获取正确的endpoint名称

**2. 认证失败**

某些Space需要Hugging Face Token:

```python
client = Client(
    "Mengnankk/deepseek-ai-DeepSeek-V3.1-test",
    hf_token="your_huggingface_token"
)
```

**3. 响应格式不匹配**

根据实际返回调整解析逻辑:

```python
def _parse_response(self, result):
    # 根据实际返回格式解析
    if isinstance(result, dict):
        return result.get('response', str(result))
    return str(result)
```

## 推荐配置(生产环境)

对于稳定的生产环境,建议:

1. **自托管模型**: 使用Ollama或vLLM部署本地模型
2. **商用API**: 使用DeepSeek官方API或OpenAI API
3. **混合方案**: 主用商用API,降级到本地模型

配置示例:

```python
# app/core/config.py
class Settings(BaseSettings):
    LLM_PROVIDER: str = "deepseek"  # deepseek | openai | ollama
    DEEPSEEK_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
```
