#!/usr/bin/env python3
"""
Redis配置初始化脚本
设置系统默认配置，确保系统设置页面有数据显示
"""
import asyncio
import json
from app.core.redis_client import get_redis
from app.services.redis_utils import redis_config_manager
import logging

logger = logging.getLogger(__name__)

async def init_redis_config():
    """初始化Redis配置"""
    try:
        redis = await get_redis()
        
        # 测试Redis连接
        await redis.ping()
        print("✅ Redis连接成功")
        
        # 设置默认系统配置
        default_configs = {
            "system_name": "AI灵魂伙伴",
            "version": "1.0.0",
            "debug_mode": True,
            "max_sessions_per_user": 10,
            "default_prompt_version": "v1",
            "cache_ttl": 3600,
            "max_context_messages": 10,
            "session_expire_seconds": 3600,
            "llm_provider": "mock",
            "features": {
                "websocket": True,
                "streaming": True,
                "ab_testing": True,
                "analytics": True,
                "notifications": True
            }
        }
        
        # 设置A/B测试配置
        ab_test_config = {
            "enabled": True,
            "traffic_split": {"v1": 50, "v2": 50},
            "min_sample_size": 100,
            "significance_level": 0.05,
            "auto_promotion_threshold": 0.1
        }
        
        # 设置缓存配置
        cache_config = {
            "companion_cache_ttl": 3600,      # 1小时
            "llm_response_cache_ttl": 1800,   # 30分钟
            "hot_conversation_ttl": 86400,    # 24小时
            "session_cache_ttl": 7200,        # 2小时
            "max_cache_size": 10000,
            "compression_enabled": True
        }
        
        # 设置一些初始统计数据
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        initial_stats = {
            f"sessions_created:{today}": 0,
            f"messages_processed:{today}": 0,
            f"successful_responses:{today}": 0,
            f"error_responses:{today}": 0,
            f"cache_hits:{today}": 0,
            f"chat_sessions_joined:{today}": 0
        }
        
        # 保存配置到Redis
        for key, value in default_configs.items():
            await redis_config_manager.set_config(key, value)
            print(f"✅ 设置配置: {key} = {value}")
        
        await redis_config_manager.set_config("ab_test_settings", ab_test_config)
        print("✅ 设置A/B测试配置")
        
        await redis_config_manager.set_config("cache_settings", cache_config)
        print("✅ 设置缓存配置")
        
        # 设置初始统计数据
        for key, value in initial_stats.items():
            await redis.set(f"stats:{key}", value)
            await redis.expire(f"stats:{key}", 30 * 24 * 3600)  # 30天过期
        print("✅ 设置初始统计数据")
        
        # 设置Prompt版本信息
        prompt_versions = {
            "versions": ["v1", "v2"],
            "current_default": "v1"
        }
        await redis_config_manager.set_config("prompt_versions", prompt_versions)
        print("✅ 设置Prompt版本信息")
        
        print("\n🎉 Redis配置初始化完成！")
        print("现在系统设置页面应该能正常显示数据了。")
        
    except Exception as e:
        print(f"❌ Redis配置初始化失败: {e}")
        logger.error(f"Redis配置初始化失败: {e}")

if __name__ == "__main__":
    asyncio.run(init_redis_config())
