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

        # 根据真实人设关键词识别角色并返回对应风格的回复
        # 林梓汐 - 逻辑、数据、普罗米修斯
        if "林梓汐" in system_prompt or "普罗米修斯" in system_prompt or ("逻辑" in system_prompt and "量化" in system_prompt):
            return self._get_linzixi_response(user_message)

        # 雪见 - 安全、零信任、防火墙
        elif "雪见" in system_prompt or ("零信任" in system_prompt) or ("安全主管" in system_prompt):
            return self._get_xuejian_response(user_message)

        # 凪 - VTuber、直播、画师
        elif "凪" in system_prompt or "VTuber" in system_prompt or ("直播" in system_prompt and "创作" in system_prompt):
            return self._get_nagi_response(user_message)

        # 时雨 - 历史、档案、诗意
        elif "时雨" in system_prompt or ("档案" in system_prompt and "历史" in system_prompt):
            return self._get_shiyu_response(user_message)

        # Zoe - CEO、硅谷、竞争
        elif "Zoe" in system_prompt or ("CEO" in system_prompt and "硅谷" in system_prompt):
            return self._get_zoe_response(user_message)

        # Kevin - DevOps、哥们、游戏
        elif "凯文" in system_prompt or "Kevin" in system_prompt or ("DevOps" in system_prompt and "哥们" in system_prompt):
            return self._get_kevin_response(user_message)

        # 旧的通用回复（兼容性）
        elif "温柔" in system_prompt or "倾听" in system_prompt:
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
