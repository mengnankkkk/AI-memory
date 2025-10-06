"""
配置管理API
提供系统配置动态修改、A/B测试配置、缓存设置等功能
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
from app.services.redis_utils import redis_config_manager
from app.services.notification import notification_service
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/config", tags=["config"])

@router.get("/all")
async def get_all_configs():
    """获取所有配置"""
    try:
        configs = await redis_config_manager.get_all_configs()
        return {"configs": configs}
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取配置失败")

@router.get("/{key}")
async def get_config(key: str):
    """获取指定配置"""
    try:
        value = await redis_config_manager.get_config(key)
        if value is None:
            raise HTTPException(status_code=404, detail="配置不存在")
        return {"key": key, "value": value}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取配置失败")

@router.post("/{key}")
async def set_config(
    key: str, 
    value: Any = Body(..., embed=True),
    ttl: Optional[int] = Body(None, embed=True)
):
    """设置配置"""
    try:
        await redis_config_manager.set_config(key, value, ttl)
        
        # 发送配置更新通知
        await notification_service.send_system_maintenance(
            f"系统配置 {key} 已更新"
        )
        
        return {"message": f"配置 {key} 设置成功"}
    except Exception as e:
        logger.error(f"设置配置失败: {e}")
        raise HTTPException(status_code=500, detail="设置配置失败")

@router.delete("/{key}")
async def delete_config(key: str):
    """删除配置"""
    try:
        success = await redis_config_manager.delete_config(key)
        if not success:
            raise HTTPException(status_code=404, detail="配置不存在")
        return {"message": f"配置 {key} 删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除配置失败: {e}")
        raise HTTPException(status_code=500, detail="删除配置失败")

@router.get("/ab-test/settings")
async def get_ab_test_settings():
    """获取A/B测试配置"""
    try:
        settings = await redis_config_manager.get_config("ab_test_settings") or {
            "enabled": True,
            "traffic_split": {"v1": 50, "v2": 50},
            "min_sample_size": 100,
            "significance_level": 0.05,
            "auto_promotion_threshold": 0.1
        }
        return {"ab_test_settings": settings}
    except Exception as e:
        logger.error(f"获取A/B测试配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取A/B测试配置失败")

@router.post("/ab-test/settings")
async def update_ab_test_settings(
    settings: Dict[str, Any] = Body(...)
):
    """更新A/B测试配置"""
    try:
        # 验证配置格式
        required_keys = ["enabled", "traffic_split", "min_sample_size"]
        for key in required_keys:
            if key not in settings:
                raise HTTPException(status_code=400, detail=f"缺少必要配置: {key}")
        
        await redis_config_manager.set_config("ab_test_settings", settings)
        
        # 通知A/B测试配置更新
        await notification_service.send_system_maintenance(
            "A/B测试配置已更新，新配置将在下次对话时生效"
        )
        
        return {"message": "A/B测试配置更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新A/B测试配置失败: {e}")
        raise HTTPException(status_code=500, detail="更新A/B测试配置失败")

@router.get("/cache/settings")
async def get_cache_settings():
    """获取缓存配置"""
    try:
        settings = await redis_config_manager.get_config("cache_settings") or {
            "companion_cache_ttl": 3600,      # 1小时
            "llm_response_cache_ttl": 1800,   # 30分钟
            "hot_conversation_ttl": 86400,    # 24小时
            "session_cache_ttl": 7200,        # 2小时
            "max_cache_size": 10000,
            "compression_enabled": True
        }
        return {"cache_settings": settings}
    except Exception as e:
        logger.error(f"获取缓存配置失败: {e}")
        raise HTTPException(status_code=500, detail="获取缓存配置失败")

@router.post("/cache/settings")
async def update_cache_settings(
    settings: Dict[str, Any] = Body(...)
):
    """更新缓存配置"""
    try:
        await redis_config_manager.set_config("cache_settings", settings)
        
        # 清理现有缓存以应用新配置
        redis = await redis_config_manager.get_redis_client()
        await redis.flushdb()
        
        await notification_service.send_system_maintenance(
            "缓存配置已更新，缓存已清理重建"
        )
        
        return {"message": "缓存配置更新成功"}
    except Exception as e:
        logger.error(f"更新缓存配置失败: {e}")
        raise HTTPException(status_code=500, detail="更新缓存配置失败")

@router.post("/cache/clear")
async def clear_cache(
    cache_type: str = Body(..., embed=True)
):
    """清理指定类型的缓存"""
    try:
        patterns = {
            "all": "*",
            "companions": "companion:*",
            "llm_responses": "llm_cache:*",
            "hot_conversations": "hot_conv:*",
            "sessions": "session:*",
            "analytics": "analytics:*"
        }
        
        if cache_type not in patterns:
            raise HTTPException(status_code=400, detail="无效的缓存类型")
        
        pattern = patterns[cache_type]
        
        if cache_type == "all":
            redis = await redis_config_manager.get_redis_client()
            await redis.flushdb()
            cleared_count = "all"
        else:
            redis = await redis_config_manager.get_redis_client()
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
            cleared_count = len(keys) if keys else 0
        
        await notification_service.send_system_maintenance(
            f"已清理 {cache_type} 缓存，清理数量: {cleared_count}"
        )
        
        return {
            "message": f"{cache_type} 缓存清理成功",
            "cleared_count": cleared_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清理缓存失败: {e}")
        raise HTTPException(status_code=500, detail="清理缓存失败")

@router.get("/system/status")
async def get_system_status():
    """获取系统状态"""
    try:
        # Redis状态
        redis = await redis_config_manager.get_redis_client()
        redis_info = await redis.info()
        
        # 连接状态
        connection_count = notification_service.get_connection_count()
        
        # 缓存统计
        cache_keys = await redis.dbsize()
        
        status = {
            "redis": {
                "connected": True,
                "memory_usage": redis_info.get("used_memory_human", "N/A"),
                "keys_count": cache_keys,
                "uptime": redis_info.get("uptime_in_seconds", 0)
            },
            "websocket": {
                "active_connections": connection_count
            },
            "cache": {
                "total_keys": cache_keys
            }
        }
        
        return {"system_status": status}
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return {
            "system_status": {
                "redis": {"connected": False, "error": str(e)},
                "websocket": {"active_connections": 0},
                "cache": {"total_keys": 0}
            }
        }
