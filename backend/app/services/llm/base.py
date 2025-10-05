"""
LLM服务基类
定义统一的接口规范
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseLLMService(ABC):
    """LLM服务抽象基类"""

    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        调用LLM完成对话

        Args:
            messages: 消息历史 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            模型回复内容
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """返回提供商名称"""
        pass

    def _build_history(self, messages: List[Dict[str, str]]) -> List[List[str]]:
        """
        将消息列表转换为Gradio格式的history
        [[user_msg, assistant_msg], ...]
        """
        history = []
        temp_pair = [None, None]

        for msg in messages:
            if msg["role"] == "user":
                temp_pair[0] = msg["content"]
            elif msg["role"] == "assistant":
                temp_pair[1] = msg["content"]
                history.append(temp_pair.copy())
                temp_pair = [None, None]

        return history
