"""
系统统计API
提供实时统计数据、性能指标、使用情况分析等
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from app.services.redis_utils import redis_stats_manager, redis_session_manager
from app.services.analytics import analytics_service
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/overview")
async def get_stats_overview():
    """获取系统统计概览"""
    try:
        # 获取今日统计
        today = datetime.now().strftime("%Y-%m-%d")
        
        stats = {
            "sessions_created": await redis_stats_manager.get_stats("sessions_created", days=1),
            "messages_processed": await redis_stats_manager.get_stats("messages_processed", days=1),
            "successful_responses": await redis_stats_manager.get_stats("successful_responses", days=1),
            "error_responses": await redis_stats_manager.get_stats("error_responses", days=1),
            "cache_hits": await redis_stats_manager.get_stats("cache_hits", days=1),
            "chat_sessions_joined": await redis_stats_manager.get_stats("chat_sessions_joined", days=1),
        }
        
        # 计算今日总数
        today_stats = {}
        for key, value in stats.items():
            today_stats[key] = value.get(today, 0)
        
        return {
            "today": today_stats,
            "trends": stats
        }
    except Exception as e:
        logger.error(f"获取统计概览失败: {e}")
        raise HTTPException(status_code=500, detail="获取统计数据失败")

@router.get("/metrics/{metric}")
async def get_metric_history(
    metric: str, 
    days: int = Query(7, ge=1, le=30)
):
    """获取指定指标的历史数据"""
    try:
        data = await redis_stats_manager.get_stats(metric, days=days)
        return {
            "metric": metric,
            "days": days,
            "data": data
        }
    except Exception as e:
        logger.error(f"获取指标历史失败: {e}")
        raise HTTPException(status_code=500, detail="获取指标数据失败")

@router.get("/prompt-usage")
async def get_prompt_usage_stats():
    """获取 Prompt 使用统计"""
    try:
        # 这里可以从 analytics_service 获取更详细的 Prompt 使用统计
        prompt_stats = await redis_stats_manager.get_stats("prompt_usage", days=7)
        return {
            "prompt_usage": prompt_stats,
            "total_usage": sum(prompt_stats.values())
        }
    except Exception as e:
        logger.error(f"获取 Prompt 使用统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取 Prompt 统计失败")

@router.get("/performance")
async def get_performance_stats():
    """获取性能统计"""
    try:
        cache_hits = await redis_stats_manager.get_stats("cache_hits", days=1)
        total_responses = await redis_stats_manager.get_stats("successful_responses", days=1)
        error_responses = await redis_stats_manager.get_stats("error_responses", days=1)
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        cache_hit_count = cache_hits.get(today, 0)
        success_count = total_responses.get(today, 0)
        error_count = error_responses.get(today, 0)
        
        # 计算缓存命中率和成功率
        total_requests = success_count + error_count
        cache_hit_rate = (cache_hit_count / success_count) * 100 if success_count > 0 else 0
        success_rate = (success_count / total_requests) * 100 if total_requests > 0 else 0
        
        return {
            "cache_hit_rate": round(cache_hit_rate, 2),
            "success_rate": round(success_rate, 2),
            "total_requests": total_requests,
            "cache_hits": cache_hit_count,
            "successful_responses": success_count,
            "error_responses": error_count
        }
    except Exception as e:
        logger.error(f"获取性能统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取性能数据失败")

@router.get("/active-sessions")
async def get_active_sessions():
    """获取活跃会话统计"""
    try:
        # 这里可以通过 Redis 查询活跃会话
        # 暂时返回一个示例结构
        return {
            "active_sessions": 0,
            "total_users": 0,
            "avg_session_duration": 0
        }
    except Exception as e:
        logger.error(f"获取活跃会话统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取活跃会话数据失败")
