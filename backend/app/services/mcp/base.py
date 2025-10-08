"""
MCP - Base Provider
定义所有情境提供者的通用接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseContextProvider(ABC):
    """
    所有情境提供者的抽象基类
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供者的唯一名称 (e.g., 'weather', 'news')"""
        pass

    @abstractmethod
    async def get_context(self, user_id: str, companion_id: int) -> Dict[str, Any]:
        """
        获取情境信息
        
        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            
        Returns:
            一个包含情境数据的字典
        """
        pass
