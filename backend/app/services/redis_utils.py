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


class RedisAffinityManager:
    """Redis好感度系统管理器"""
    
    def __init__(self):
        self.affinity_prefix = "affinity"
        self.state_prefix = "companion_state"
        self.event_prefix = "event"
        self.relationship_expire = 30 * 24 * 3600  # 30天过期
    
    async def init_companion_state(self, user_id: str, companion_id: int):
        """初始化伙伴状态"""
        try:
            redis = await get_redis()
            state_key = f"{self.state_prefix}:{user_id}:{companion_id}"
            
            # 检查是否已存在
            existing_state = await redis.get(state_key)
            if existing_state:
                return json.loads(existing_state)
            
            # 初始化状态
            initial_state = {
                "affinity_score": 50,  # 初始好感度
                "trust_score": 10,     # 信任度
                "tension_score": 0,    # 紧张度
                "romance_level": "初识", # 关系阶段
                "current_mood": "平静",  # 当前心情
                "mood_last_updated": int(time.time()),
                "last_interaction_at": int(time.time()),
                "total_interactions": 0,
                "days_since_first_meet": 0,
                "special_events_triggered": [],
                "gifts_received": [],
                "outfit_unlocked": ["default"],
                "memories": []
            }
            
            await redis.setex(state_key, self.relationship_expire, json.dumps(initial_state))
            return initial_state
        except Exception as e:
            logger.error(f"[init_companion_state] {e}")
            return None

    async def get_companion_state(self, user_id: str, companion_id: int) -> Optional[Dict]:
        """获取伙伴状态"""
        try:
            redis = await get_redis()
            state_key = f"{self.state_prefix}:{user_id}:{companion_id}"
            state_data = await redis.get(state_key)
            if state_data:
                return json.loads(state_data)
            # 如果不存在，初始化
            return await self.init_companion_state(user_id, companion_id)
        except Exception as e:
            logger.error(f"[get_companion_state] {e}")
            return None

    async def update_affinity(self, user_id: str, companion_id: int, affinity_change: int, 
                            trust_change: int = 0, tension_change: int = 0, 
                            interaction_type: str = "chat"):
        """更新好感度和状态"""
        try:
            state = await self.get_companion_state(user_id, companion_id)
            if not state:
                return False
            
            # 更新数值
            state["affinity_score"] = max(0, min(1000, state["affinity_score"] + affinity_change))
            state["trust_score"] = max(0, min(100, state["trust_score"] + trust_change))
            state["tension_score"] = max(0, min(100, state["tension_score"] + tension_change))
            state["total_interactions"] += 1
            state["last_interaction_at"] = int(time.time())
            
            # 更新关系阶段
            new_level = self._calculate_romance_level(state["affinity_score"])
            if new_level != state["romance_level"]:
                state["romance_level"] = new_level
                # 关系升级事件
                await self._trigger_relationship_upgrade_event(user_id, companion_id, new_level)
            
            # 更新心情
            state["current_mood"] = self._calculate_mood(state, interaction_type)
            state["mood_last_updated"] = int(time.time())
            
            # 保存状态
            redis = await get_redis()
            state_key = f"{self.state_prefix}:{user_id}:{companion_id}"
            await redis.setex(state_key, self.relationship_expire, json.dumps(state))
            
            return True
        except Exception as e:
            logger.error(f"[update_affinity] {e}")
            return False

    def _calculate_romance_level(self, affinity_score: int) -> str:
        """根据好感度计算关系阶段"""
        if affinity_score < 100:
            return "初识"
        elif affinity_score < 200:
            return "朋友"
        elif affinity_score < 350:
            return "好朋友"
        elif affinity_score < 500:
            return "特别的人"
        elif affinity_score < 700:
            return "心动"
        elif affinity_score < 850:
            return "恋人"
        else:
            return "深爱"

    def _calculate_mood(self, state: Dict, interaction_type: str) -> str:
        """计算AI心情"""
        affinity = state["affinity_score"]
        tension = state["tension_score"]
        
        if tension > 60:
            return "生气" if affinity < 300 else "委屈"
        elif tension > 30:
            return "困惑" if affinity < 200 else "不安"
        elif affinity > 700:
            return "幸福" if interaction_type == "gift" else "开心"
        elif affinity > 400:
            return "开心" if interaction_type in ["compliment", "care"] else "愉快"
        elif affinity > 200:
            return "愉快" if interaction_type == "chat" else "平静"
        else:
            return "平静"

    async def _trigger_relationship_upgrade_event(self, user_id: str, companion_id: int, new_level: str):
        """触发关系升级事件"""
        try:
            redis = await get_redis()
            event_key = f"{self.event_prefix}:upgrade:{user_id}:{companion_id}:{int(time.time())}"
            event_data = {
                "type": "relationship_upgrade",
                "new_level": new_level,
                "triggered_at": int(time.time()),
                "user_id": user_id,
                "companion_id": companion_id
            }
            await redis.setex(event_key, 24 * 3600, json.dumps(event_data))  # 24小时过期
        except Exception as e:
            logger.error(f"[_trigger_relationship_upgrade_event] {e}")

    async def add_memory(self, user_id: str, companion_id: int, memory_text: str, memory_type: str = "conversation"):
        """添加记忆"""
        try:
            state = await self.get_companion_state(user_id, companion_id)
            if not state:
                return False
            
            memory = {
                "content": memory_text,
                "type": memory_type,
                "timestamp": int(time.time()),
                "importance": self._calculate_memory_importance(memory_text, state)
            }
            
            state["memories"].append(memory)
            
            # 保持最多100条记忆，按重要性排序
            state["memories"] = sorted(state["memories"], key=lambda x: x["importance"], reverse=True)[:100]
            
            # 保存状态
            redis = await get_redis()
            state_key = f"{self.state_prefix}:{user_id}:{companion_id}"
            await redis.setex(state_key, self.relationship_expire, json.dumps(state))
            
            return True
        except Exception as e:
            logger.error(f"[add_memory] {e}")
            return False

    def _calculate_memory_importance(self, memory_text: str, state: Dict) -> float:
        """计算记忆重要性"""
        base_importance = 0.5
        
        # 关键词提升重要性
        important_keywords = ["喜欢", "爱", "讨厌", "生气", "开心", "伤心", "生日", "约会", "礼物"]
        for keyword in important_keywords:
            if keyword in memory_text:
                base_importance += 0.2
        
        # 关系阶段提升重要性
        if state["romance_level"] in ["恋人", "深爱"]:
            base_importance += 0.3
        
        return min(1.0, base_importance)

    async def give_gift(self, user_id: str, companion_id: int, gift_type: str, gift_name: str):
        """赠送礼物"""
        try:
            state = await self.get_companion_state(user_id, companion_id)
            if not state:
                return False
            
            # 记录礼物
            gift_record = {
                "type": gift_type,
                "name": gift_name,
                "given_at": int(time.time())
            }
            state["gifts_received"].append(gift_record)
            
            # 根据礼物类型增加好感度
            gift_affinity_map = {
                "flower": 15,
                "chocolate": 10,
                "jewelry": 25,
                "book": 8,
                "game": 12,
                "outfit": 20
            }
            
            affinity_gain = gift_affinity_map.get(gift_type, 5)
            await self.update_affinity(user_id, companion_id, affinity_gain, 
                                     trust_change=2, interaction_type="gift")
            
            return True
        except Exception as e:
            logger.error(f"[give_gift] {e}")
            return False

class RedisEventManager:
    """Redis事件管理器"""
    
    def __init__(self):
        self.event_queue_prefix = "event_queue"
        self.event_history_prefix = "event_history"
        self.daily_events_prefix = "daily_events"
    
    async def trigger_random_event(self, user_id: str, companion_id: int) -> Optional[Dict]:
        """触发随机事件"""
        try:
            redis = await get_redis()
            affinity_manager = RedisAffinityManager()
            
            # 获取伙伴状态
            state = await affinity_manager.get_companion_state(user_id, companion_id)
            if not state:
                return None
            
            # 根据状态选择合适的事件
            available_events = self._get_available_events(state)
            if not available_events:
                return None
            
            import random
            selected_event = random.choice(available_events)
            
            # 记录事件
            event_key = f"{self.event_queue_prefix}:{user_id}:{companion_id}"
            await redis.lpush(event_key, json.dumps(selected_event))
            await redis.expire(event_key, 24 * 3600)  # 24小时过期
            
            return selected_event
        except Exception as e:
            logger.error(f"[trigger_random_event] {e}")
            return None

    def _get_available_events(self, state: Dict) -> List[Dict]:
        """获取可用事件列表"""
        romance_level = state["romance_level"]
        affinity = state["affinity_score"]
        mood = state["current_mood"]
        
        events = []
        
        # 基础事件（所有阶段可用）
        basic_events = [
            {
                "type": "weather_talk",
                "title": "天气聊天",
                "description": "想和你聊聊今天的天气",
                "affinity_requirement": 0
            },
            {
                "type": "hobby_share",
                "title": "兴趣分享",
                "description": "想分享一个有趣的发现",
                "affinity_requirement": 50
            }
        ]
        
        # 朋友阶段事件
        friend_events = [
            {
                "type": "movie_recommendation",
                "title": "电影推荐",
                "description": "想推荐一部好看的电影给你",
                "affinity_requirement": 150
            },
            {
                "type": "cooking_together",
                "title": "一起做饭",
                "description": "想和你一起尝试做一道新菜",
                "affinity_requirement": 180
            }
        ]
        
        # 恋人阶段事件
        romantic_events = [
            {
                "type": "virtual_date",
                "title": "虚拟约会",
                "description": "想和你来一次特别的约会",
                "affinity_requirement": 500
            },
            {
                "type": "confession",
                "title": "表白时刻",
                "description": "有些话想对你说...",
                "affinity_requirement": 600
            }
        ]
        
        # 筛选符合条件的事件
        all_events = basic_events + friend_events + romantic_events
        for event in all_events:
            if affinity >= event["affinity_requirement"]:
                events.append(event)
        
        return events

    async def get_pending_events(self, user_id: str, companion_id: int) -> List[Dict]:
        """获取待处理事件"""
        try:
            redis = await get_redis()
            event_key = f"{self.event_queue_prefix}:{user_id}:{companion_id}"
            events = await redis.lrange(event_key, 0, -1)
            return [json.loads(event) for event in events] if events else []
        except Exception as e:
            logger.error(f"[get_pending_events] {e}")
            return []

# 全局实例
redis_session_manager = RedisSessionManager()
redis_stats_manager = RedisStatsManager()
redis_config_manager = RedisConfigManager()
redis_affinity_manager = RedisAffinityManager()
redis_event_manager = RedisEventManager()
