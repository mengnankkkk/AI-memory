"""
Redis优化工具类
提供会话管理、统计数据、系统配置等Redis操作
"""
import json
import logging
from typing import Dict, List, Optional, Any
from app.core.redis_client import get_redis
import time

logger = logging.getLogger("redis_utils")

class RedisSessionManager:
    """Redis会话管理器"""
    
    def __init__(self):
        self.session_prefix = "session"
        self.user_sessions_prefix = "user_sessions"
        self.session_expire = 3600  # 1小时
    
    async def create_session(self, session_id: str, user_id: str, companion_id: int, data: Optional[Dict] = None):
        """创建会话"""
        try:
            redis = await get_redis()
            session_data = {
                "user_id": user_id,
                "companion_id": companion_id,
                "created_at": int(time.time()),
                "last_activity": int(time.time()),
                **(data or {})
            }
            session_key = f"{self.session_prefix}:{session_id}"
            await redis.setex(session_key, self.session_expire, json.dumps(session_data))
            
            # 添加到用户会话列表
            user_sessions_key = f"{self.user_sessions_prefix}:{user_id}"
            await redis.sadd(user_sessions_key, session_id)
            await redis.expire(user_sessions_key, self.session_expire)
        except Exception as e:
            logger.error(f"[create_session] {e}")

    async def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话信息"""
        try:
            redis = await get_redis()
            session_key = f"{self.session_prefix}:{session_id}"
            session_data = await redis.get(session_key)
            if session_data:
                return json.loads(session_data)
            return None
        except Exception as e:
            logger.error(f"[get_session] {e}")
            return None

    async def update_session_activity(self, session_id: str):
        """更新会话活跃时间"""
        try:
            redis = await get_redis()
            session_key = f"{self.session_prefix}:{session_id}"
            session_data = await self.get_session(session_id)
            if session_data:
                session_data["last_activity"] = int(time.time())
                await redis.setex(session_key, self.session_expire, json.dumps(session_data))
        except Exception as e:
            logger.error(f"[update_session_activity] {e}")

    async def get_user_sessions(self, user_id: str) -> List[str]:
        """获取用户的所有会话"""
        try:
            redis = await get_redis()
            user_sessions_key = f"{self.user_sessions_prefix}:{user_id}"
            sessions = await redis.smembers(user_sessions_key)
            return list(sessions) if sessions else []
        except Exception as e:
            logger.error(f"[get_user_sessions] {e}")
            return []

    async def cleanup_expired_sessions(self):
        """清理过期会话"""
        try:
            redis = await get_redis()
            # 目前Redis的TTL自动处理过期
        except Exception as e:
            logger.error(f"[cleanup_expired_sessions] {e}")

class RedisStatsManager:
    """Redis统计数据管理器"""
    
    def __init__(self):
        self.stats_prefix = "stats"
        self.daily_stats_expire = 30 * 24 * 3600  # 30天
    
    async def increment_counter(self, metric: str, value: int = 1, date: Optional[str] = None):
        """增加计数器"""
        try:
            redis = await get_redis()
            if not date:
                from datetime import datetime
                date = datetime.now().strftime("%Y-%m-%d")
            key = f"{self.stats_prefix}:{metric}:{date}"
            await redis.incrby(key, value)
            await redis.expire(key, self.daily_stats_expire)
        except Exception as e:
            logger.error(f"[increment_counter] {e}")

    async def set_gauge(self, metric: str, value: float, date: Optional[str] = None):
        """设置指标值"""
        try:
            redis = await get_redis()
            if not date:
                from datetime import datetime
                date = datetime.now().strftime("%Y-%m-%d")
            key = f"{self.stats_prefix}:{metric}:{date}"
            await redis.set(key, value)
            await redis.expire(key, self.daily_stats_expire)
        except Exception as e:
            logger.error(f"[set_gauge] {e}")

    async def get_stats(self, metric: str, days: int = 7) -> Dict[str, int]:
        """获取统计数据"""
        try:
            redis = await get_redis()
            from datetime import datetime, timedelta
            stats = {}
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                key = f"{self.stats_prefix}:{metric}:{date}"
                value = await redis.get(key)
                stats[date] = int(value) if value else 0
            return stats
        except Exception as e:
            logger.error(f"[get_stats] {e}")
            return {}

class RedisConfigManager:
    """Redis系统配置管理器"""
    
    def __init__(self):
        self.config_prefix = "config"
        self.config_expire = 24 * 3600  # 24小时
    
    async def set_config(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置配置"""
        try:
            redis = await get_redis()
            config_key = f"{self.config_prefix}:{key}"
            expire_time = ttl or self.config_expire
            await redis.setex(config_key, expire_time, json.dumps(value))
        except Exception as e:
            logger.error(f"[set_config] {e}")

    async def delete_config(self, key: str) -> bool:
        """删除配置"""
        try:
            redis = await get_redis()
            config_key = f"{self.config_prefix}:{key}"
            result = await redis.delete(config_key)
            return result > 0
        except Exception as e:
            logger.error(f"[delete_config] {e}")
            return False

    async def get_redis_client(self):
        """获取Redis客户端"""
        try:
            return await get_redis()
        except Exception as e:
            logger.error(f"[get_redis_client] {e}")
            return None

    async def get_config(self, key: str, default=None) -> Any:
        """获取配置"""
        try:
            redis = await get_redis()
            config_key = f"{self.config_prefix}:{key}"
            value = await redis.get(config_key)
            if value:
                return json.loads(value)
            return default
        except Exception as e:
            logger.error(f"[get_config] {e}")
            return default

    async def get_all_configs(self) -> Dict[str, Any]:
        """获取所有配置"""
        try:
            redis = await get_redis()
            keys = await redis.keys(f"{self.config_prefix}:*")
            configs = {}
            for key in keys:
                config_name = key.split(":")[-1]
                value = await redis.get(key)
                if value:
                    configs[config_name] = json.loads(value)
            return configs
        except Exception as e:
            logger.error(f"[get_all_configs] {e}")
            return {}


# 全局实例
redis_session_manager = RedisSessionManager()
redis_stats_manager = RedisStatsManager()
redis_config_manager = RedisConfigManager()
