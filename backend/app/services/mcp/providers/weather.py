"""
MCP - Weather Provider
提供天气情境信息
"""
from typing import Dict, Any
from ..base import BaseContextProvider

class WeatherProvider(BaseContextProvider):
    """
    天气情境提供者 (模拟)
    """
    
    @property
    def provider_name(self) -> str:
        return "weather"

    async def get_context(self, user_id: str, companion_id: int) -> Dict[str, Any]:
        """
        获取天气数据 (模拟)
        在真实实现中，这里会调用天气API
        """
        # 模拟API调用
        print(f"WeatherProvider: Fetching weather for user {user_id}")
        
        # 模拟不同用户看到不同天气
        if user_id == "test_user_123":
            return {
                "temperature": 23.5,
                "condition": "小雨",
                "city": "上海"
            }
        else:
            return {
                "temperature": 31.0,
                "condition": "晴",
                "city": "北京"
            }
