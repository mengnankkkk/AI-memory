"""
Mock LLM服务实现
用于测试和演示
"""
from typing import List, Dict
import asyncio
import random
from app.services.llm.base import BaseLLMService


class MockLLMService(BaseLLMService):
    """Mock模式LLM服务"""

    def __init__(self):
        super().__init__(api_url="mock://local")
        print("⚠️  当前使用Mock模式，回复为模拟内容")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """返回基于性格的模拟回复"""
        # 获取系统提示词和最后一条用户消息
        system_prompt = ""
        user_message = ""

        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            elif msg["role"] == "user":
                user_message = msg["content"]

        # 模拟API延迟
        await asyncio.sleep(0.5)

        # 根据性格原型返回不同风格的回复
        if "温柔" in system_prompt or "倾听" in system_prompt:
            return self._get_listener_response(user_message)
        elif "元气" in system_prompt or "鼓励" in system_prompt:
            return self._get_cheerleader_response(user_message)
        elif "理性" in system_prompt or "分析" in system_prompt:
            return self._get_analyst_response(user_message)
        else:
            return f"我听到你说: {user_message}\n\n这是Mock模式的回复。"

    def _get_listener_response(self, message: str) -> str:
        """温柔倾听者的回复"""
        responses = [
            f"我听到你说{message}了。听起来你现在的心情怎么样呢？💖",
            f"嗯嗯，我理解你的感受。能和我详细说说吗？",
            f"谢谢你愿意和我分享这些。你一定经历了很多吧。",
        ]
        return random.choice(responses)

    def _get_cheerleader_response(self, message: str) -> str:
        """元气鼓励者的回复"""
        responses = [
            f"哇！听你这么说我也充满能量了！✨继续加油哦！",
            f"太棒了！你真的很厉害！💪这样的态度一定会成功的！",
            f"耶！我就知道你可以的！🎉保持这份热情，未来一定很精彩！",
        ]
        return random.choice(responses)

    def _get_analyst_response(self, message: str) -> str:
        """理性分析者的回复"""
        responses = [
            f"关于你提到的问题，我们可以从几个角度来分析：首先...其次...最后...",
            f"这是一个很有意思的话题。让我们理性地思考一下其中的逻辑。",
            f"从你的描述来看，这个情况包含几个关键因素。我们一一分析。",
        ]
        return random.choice(responses)

    def get_provider_name(self) -> str:
        return "Mock Service"
