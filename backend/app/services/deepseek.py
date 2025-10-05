from gradio_client import Client
from typing import AsyncIterator, List, Dict
import asyncio
from app.core.config import settings


class DeepSeekService:
    """DeepSeek模型服务"""

    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """初始化Gradio客户端"""
        try:
            self.client = Client("Mengnankk/deepseek-ai-DeepSeek-V3.1-test")
            print("✓ DeepSeek客户端初始化成功")
        except Exception as e:
            print(f"✗ DeepSeek客户端初始化失败: {e}")
            self.client = None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> str:
        """
        调用DeepSeek完成对话

        Args:
            messages: 消息历史 [{"role": "user/assistant/system", "content": "..."}]
            stream: 是否流式输出

        Returns:
            模型回复内容
        """
        if not self.client:
            return "抱歉,模型服务暂时不可用,请稍后再试。"

        try:
            # 构建提示词
            prompt = self._build_prompt(messages)

            # 调用API (根据实际API调整)
            # 注意: 这里需要根据实际的Gradio API调整参数
            result = await asyncio.to_thread(
                self.client.predict,
                prompt,
                api_name="/chat"  # 根据实际API endpoint调整
            )

            return result
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            return f"抱歉,我遇到了一些问题: {str(e)}"

    def _build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        构建完整提示词

        将对话历史转换为模型可理解的格式
        """
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

        prompt_parts.append("助手:")  # 触发模型回复

        return "\n\n".join(prompt_parts)


# 全局单例
deepseek_service = DeepSeekService()
