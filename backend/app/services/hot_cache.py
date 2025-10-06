"""
热门对话缓存服务
缓存高频对话模式和回复，提升响应速度
"""
import hashlib
import json
from typing import List, Dict, Optional
from app.core.redis_client import get_redis

class HotConversationCache:
    """热门对话缓存管理"""
    
    def __init__(self):
        self.cache_prefix = "hot_conv"
        self.pattern_prefix = "conv_pattern"
        self.expire_time = 3600  # 1小时过期
    
    async def get_conversation_pattern_key(self, personality: str, user_input: str) -> str:
        """生成对话模式的缓存key"""
        # 简化用户输入，提取关键词
        normalized_input = self._normalize_input(user_input)
        raw_key = f"{personality}:{normalized_input}"
        return hashlib.md5(raw_key.encode()).hexdigest()
    
    def _normalize_input(self, user_input: str) -> str:
        """简化和标准化用户输入"""
        # 去除标点符号和多余空格
        import re
        normalized = re.sub(r'[^\w\s]', '', user_input.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # 提取关键词（简单实现，可用更复杂的NLP处理）
        keywords = normalized.split()[:5]  # 取前5个词
        return ' '.join(keywords)
    
    async def get_cached_response(self, personality: str, user_input: str) -> Optional[str]:
        """获取缓存的热门回复"""
        redis = await get_redis()
        pattern_key = await self.get_conversation_pattern_key(personality, user_input)
        cache_key = f"{self.cache_prefix}:{pattern_key}"
        
        cached_response = await redis.get(cache_key)
        if cached_response:
            # 更新热度
            await self._increment_pattern_heat(pattern_key)
            return cached_response
        
        return None
    
    async def cache_response(self, personality: str, user_input: str, response: str):
        """缓存对话回复"""
        redis = await get_redis()
        pattern_key = await self.get_conversation_pattern_key(personality, user_input)
        cache_key = f"{self.cache_prefix}:{pattern_key}"
        
        # 检查是否已存在，如果存在则更新热度
        existing = await redis.get(cache_key)
        if existing:
            await self._increment_pattern_heat(pattern_key)
        else:
            # 新缓存
            await redis.setex(cache_key, self.expire_time, response)
            await self._set_pattern_heat(pattern_key, 1)
    
    async def _increment_pattern_heat(self, pattern_key: str):
        """增加对话模式热度"""
        redis = await get_redis()
        heat_key = f"{self.pattern_prefix}:heat:{pattern_key}"
        await redis.incr(heat_key)
        await redis.expire(heat_key, self.expire_time)
    
    async def _set_pattern_heat(self, pattern_key: str, heat: int):
        """设置对话模式热度"""
        redis = await get_redis()
        heat_key = f"{self.pattern_prefix}:heat:{pattern_key}"
        await redis.setex(heat_key, self.expire_time, heat)
    
    async def get_hot_patterns(self, limit: int = 10) -> List[Dict]:
        """获取热门对话模式"""
        redis = await get_redis()
        
        # 获取所有热度keys
        heat_keys = await redis.keys(f"{self.pattern_prefix}:heat:*")
        if not heat_keys:
            return []
        
        # 获取热度值
        pattern_heats = []
        for key in heat_keys:
            heat = await redis.get(key)
            if heat:
                pattern_key = key.split(":")[-1]
                pattern_heats.append({
                    "pattern_key": pattern_key,
                    "heat": int(heat)
                })
        
        # 按热度排序
        pattern_heats.sort(key=lambda x: x["heat"], reverse=True)
        return pattern_heats[:limit]
    
    async def preload_hot_conversations(self):
        """预加载热门对话到内存"""
        hot_patterns = await self.get_hot_patterns(50)
        redis = await get_redis()
        
        preloaded = []
        for pattern in hot_patterns:
            cache_key = f"{self.cache_prefix}:{pattern['pattern_key']}"
            response = await redis.get(cache_key)
            if response:
                preloaded.append({
                    "pattern_key": pattern["pattern_key"],
                    "heat": pattern["heat"],
                    "response": response
                })
        
        return preloaded

hot_conversation_cache = HotConversationCache()
