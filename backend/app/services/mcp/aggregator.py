"""
MCP - Context Aggregator
负责动态加载所有情境提供者并汇总其数据
"""
import asyncio
import pkgutil
import importlib
from typing import Dict, Any, List
from .base_provider import BaseContextProvider

class ContextAggregator:
    """
    情境聚合器
    """
    
    def __init__(self):
        self._providers: List[BaseContextProvider] = []
        self._load_providers()

    def _load_providers(self):
        """动态加载所有可用的情境提供者"""
        # 导入providers模块
        import app.services.mcp.providers as providers_package
        
        # 遍历模块下的所有子模块
        for _, module_name, _ in pkgutil.iter_modules(providers_package.__path__):
            module = importlib.import_module(f"{providers_package.__name__}.{module_name}")
            
            # 查找模块中所有继承了BaseContextProvider的类
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, type) and issubclass(attribute, BaseContextProvider) and attribute is not BaseContextProvider:
                    # 实例化提供者并添加到列表
                    self._providers.append(attribute())
                    print(f"MCP: Loaded provider '{attribute().provider_name}' from {module_name}.py")

    async def get_full_context(self, user_id: str, companion_id: int) -> Dict[str, Any]:
        """
        并行获取所有情境提供者的数据并汇总
        """
        if not self._providers:
            return {}

        # 创建所有提供者的异步任务
        tasks = [
            provider.get_context(user_id, companion_id) for provider in self._providers
        ]
        
        # 并行执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 汇总结果
        full_context: Dict[str, Any] = {}
        for i, result in enumerate(results):
            provider_name = self._providers[i].provider_name
            if isinstance(result, Exception):
                print(f"MCP: Error fetching context from '{provider_name}': {result}")
                full_context[provider_name] = None # or some error indicator
            else:
                full_context[provider_name] = result
                
        return full_context

# 创建一个全局单例
context_aggregator = ContextAggregator()
