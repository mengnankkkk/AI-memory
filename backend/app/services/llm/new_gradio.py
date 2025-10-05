"""
新Gradio API服务实现
基于 https://haiyangpengai-careyou.ms.show/
"""
from gradio_client import Client
from typing import List, Dict
import asyncio
from app.services.llm.base import BaseLLMService


class NewGradioService(BaseLLMService):
    """新Gradio API服务"""

    def __init__(self, api_url: str = "https://haiyangpengai-careyou.ms.show/"):
        super().__init__(api_url)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """初始化Gradio客户端"""
        try:
            self.client = Client(self.api_url)
            print(f"✓ {self.get_provider_name()} 客户端初始化成功")
        except Exception as e:
            print(f"✗ {self.get_provider_name()} 客户端初始化失败: {e}")
            self.client = None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.6,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        调用新Gradio API完成对话

        使用 /generate_response_and_tts API
        """
        if not self.client:
            return "抱歉，API服务暂时不可用。"

        try:
            # 构建Gradio格式的历史记录
            history = self._build_history(messages)

            # 获取top_p参数
            top_p = kwargs.get("top_p", 0.95)

            # 调用API (根据官方文档使用关键字参数)
            result = await asyncio.to_thread(
                self.client.predict,
                history=history,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                api_name="/generate_response_and_tts"
            )

            # result是一个包含3个元素的元组
            # [0]: 更新后的history
            # [1]: 音频文件路径
            # [2]: TTS转换时间
            updated_history = result[0]

            # 提取最后一条助手回复
            if updated_history and len(updated_history) > 0:
                last_message = updated_history[-1]
                if len(last_message) > 1 and last_message[1]:
                    return last_message[1]

            return "抱歉，没有收到回复。"

        except Exception as e:
            print(f"{self.get_provider_name()} API调用失败: {e}")
            return f"抱歉，调用失败: {str(e)}"

    def get_provider_name(self) -> str:
        return "NewGradio API"
