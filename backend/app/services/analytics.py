"""
数据埋点和分析服务
记录用户行为、Prompt使用情况、对话质量等
"""
import time
import json
from datetime import datetime
from app.core.redis_client import get_redis

class AnalyticsService:
    """数据埋点服务"""
    
    @staticmethod
    async def track_prompt_usage(user_id: str, companion_id: int, prompt_version: str, personality: str):
        """记录Prompt版本使用情况"""
        redis = await get_redis()
        timestamp = int(time.time())
        event = {
            "user_id": user_id,
            "companion_id": companion_id,
            "prompt_version": prompt_version,
            "personality": personality,
            "timestamp": timestamp,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # 存储到Redis List中，便于批量处理
        await redis.lpush("analytics:prompt_usage", json.dumps(event))
        
        # 统计每日使用量
        daily_key = f"stats:prompt:{prompt_version}:{event['date']}"
        await redis.incr(daily_key)
        await redis.expire(daily_key, 7 * 24 * 3600)  # 7天过期
    
    @staticmethod
    async def track_conversation_quality(user_id: str, companion_id: int, message_id: int, 
                                       score: int, prompt_version: str):
        """记录对话质量反馈"""
        redis = await get_redis()
        timestamp = int(time.time())
        event = {
            "user_id": user_id,
            "companion_id": companion_id,
            "message_id": message_id,
            "score": score,  # 1=好评, -1=差评
            "prompt_version": prompt_version,
            "timestamp": timestamp,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        await redis.lpush("analytics:quality_feedback", json.dumps(event))
        
        # 统计Prompt版本质量得分
        quality_key = f"stats:quality:{prompt_version}:{event['date']}"
        await redis.hincrby(quality_key, "total_score", score)
        await redis.hincrby(quality_key, "feedback_count", 1)
        await redis.expire(quality_key, 7 * 24 * 3600)
    
    @staticmethod
    async def track_user_behavior(user_id: str, action: str, **kwargs):
        """记录用户行为"""
        redis = await get_redis()
        timestamp = int(time.time())
        event = {
            "user_id": user_id,
            "action": action,
            "timestamp": timestamp,
            "date": datetime.now().strftime("%Y-%m-%d"),
            **kwargs
        }
        
        await redis.lpush("analytics:user_behavior", json.dumps(event))
    
    @staticmethod
    async def get_prompt_stats(prompt_version: str, days: int = 7):
        """获取Prompt统计数据"""
        redis = await get_redis()
        stats = {"usage": {}, "quality": {}}
        
        for i in range(days):
            date = datetime.now().strftime("%Y-%m-%d")
            
            # 使用量统计
            usage_key = f"stats:prompt:{prompt_version}:{date}"
            usage = await redis.get(usage_key)
            stats["usage"][date] = int(usage) if usage else 0
            
            # 质量统计
            quality_key = f"stats:quality:{prompt_version}:{date}"
            quality_data = await redis.hgetall(quality_key)
            if quality_data:
                total_score = int(quality_data.get("total_score", 0))
                feedback_count = int(quality_data.get("feedback_count", 0))
                avg_score = total_score / feedback_count if feedback_count > 0 else 0
                stats["quality"][date] = {
                    "avg_score": avg_score,
                    "feedback_count": feedback_count
                }
            else:
                stats["quality"][date] = {"avg_score": 0, "feedback_count": 0}
        
        return stats

analytics_service = AnalyticsService()
