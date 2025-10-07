"""
DeepSeek Gradio API服务实现
基于 Hugging Face Space
"""
from gradio_client import Client
from typing import List, Dict
import asyncio
from app.services.llm.base import BaseLLMService


class DeepSeekGradioService(BaseLLMService):
    """DeepSeek Gradio API服务"""

    def __init__(self, api_url: str = "Mengnankk/deepseek-ai-DeepSeek-V3.1-test"):
        super().__init__(api_url)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """初始化Gradio客户端"""
        try:
            self.client = Client(self.api_url)
            print(f"[OK] {self.get_provider_name()} 客户端初始化成功")
        except Exception as e:
            print(f"[ERROR] {self.get_provider_name()} 客户端初始化失败: {e}")
            self.client = None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """调用DeepSeek API"""
        if not self.client:
            return "抱歉，DeepSeek API暂时不可用。"

        try:
            # 构建提示词
            prompt = self._build_prompt(messages)

            # 调用API (需要根据实际endpoint调整)
            result = await asyncio.to_thread(
                self.client.predict,
                prompt,
                api_name="/chat"  # 根据实际API调整
            )

            return result

        except Exception as e:
            print(f"{self.get_provider_name()} API调用失败: {e}")
            return f"抱歉，调用失败: {str(e)}"

    def _build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """构建完整提示词"""
        prompt_parts = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                prompt_parts.append(f"系统指令:\n{content}\n")
            elif role == "user":
                prompt_parts.append(f"用户: {content}")
            elif role == "assistant":
                prompt_parts.append(f"助手: {content}")

        prompt_parts.append("助手:")
        return "\n\n".join(prompt_parts)

    def get_provider_name(self) -> str:
        return "DeepSeek Gradio"
