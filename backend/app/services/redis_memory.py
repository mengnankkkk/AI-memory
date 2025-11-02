"""
Redis KV存储实现 - L3语义记忆系统

该模块使用Redis实现高效的用户事实存储，用于存储和管理
结构化的用户信息（昵称、职业、梦想等）。
"""
import logging
import json
from typing import Dict, Optional
from app.core.redis_client import get_redis

logger = logging.getLogger("redis_memory")


class RedisMemorySystem:
    """
    基于Redis的L3语义记忆系统实现

    存储结构：
    - key: user_facts:{user_id}:{companion_id}
    - value: JSON格式的用户事实字典

    特点：
    - 快速键值查询
    - 实时更新
    - 支持TTL过期时间
    """

    def __init__(self, expire_days: int = 180):
        """
        初始化Redis内存系统

        Args:
            expire_days: 事实数据过期天数
        """
        self.expire_seconds = expire_days * 24 * 3600
        self.key_prefix = "user_facts"
        logger.info(f"✅ Redis L3语义记忆已初始化 (过期时间: {expire_days}天)")

    def _make_key(self, user_id: str, companion_id: int) -> str:
        """生成Redis key"""
        return f"{self.key_prefix}:{user_id}:{companion_id}"

    async def get_user_facts(
        self,
        user_id: str,
        companion_id: int
    ) -> Dict[str, str]:
        """
        获取用户的结构化事实

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID

        Returns:
            用户事实字典，例如：
            {
                "昵称": "小星",
                "喜欢的颜色": "蓝色",
                "职业": "画家",
                "梦想": "举办个人画展",
                "特殊日期_生日": "1998-05-20"
            }
        """
        try:
            redis = await get_redis()
            key = self._make_key(user_id, companion_id)

            # 从Redis获取
            facts_json = await redis.get(key)
            if facts_json:
                facts = json.loads(facts_json)
                logger.info(f"✅ 获取用户事实成功 ({len(facts)} 个字段)")
                return facts

            logger.debug(f"📝 用户 {user_id} 暂无事实数据")
            return {}

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析失败: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ 获取用户事实失败: {e}")
            return {}

    async def save_user_fact(
        self,
        user_id: str,
        companion_id: int,
        fact_key: str,
        fact_value: str
    ) -> bool:
        """
        保存单个用户事实

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            fact_key: 事实的键（例如"昵称"、"职业"）
            fact_value: 事实的值

        Returns:
            是否保存成功
        """
        try:
            redis = await get_redis()
            key = self._make_key(user_id, companion_id)

            # 获取现有事实
            facts = await self.get_user_facts(user_id, companion_id)

            # 更新事实
            facts[fact_key] = fact_value

            # 保存回Redis
            await redis.setex(
                key,
                self.expire_seconds,
                json.dumps(facts, ensure_ascii=False)
            )

            logger.info(f"✅ 保存事实: {fact_key} = {fact_value}")
            return True

        except Exception as e:
            logger.error(f"❌ 保存事实失败: {e}")
            return False

    async def save_multiple_facts(
        self,
        user_id: str,
        companion_id: int,
        facts: Dict[str, str]
    ) -> bool:
        """
        一次性保存多个用户事实

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            facts: 事实字典

        Returns:
            是否保存成功
        """
        try:
            redis = await get_redis()
            key = self._make_key(user_id, companion_id)

            # 获取现有事实
            existing_facts = await self.get_user_facts(user_id, companion_id)

            # 合并新旧事实
            existing_facts.update(facts)

            # 保存回Redis
            await redis.setex(
                key,
                self.expire_seconds,
                json.dumps(existing_facts, ensure_ascii=False)
            )

            logger.info(f"✅ 批量保存 {len(facts)} 个事实")
            return True

        except Exception as e:
            logger.error(f"❌ 批量保存事实失败: {e}")
            return False

    async def delete_user_fact(
        self,
        user_id: str,
        companion_id: int,
        fact_key: str
    ) -> bool:
        """
        删除用户的某个特定事实

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            fact_key: 要删除的事实键

        Returns:
            是否删除成功
        """
        try:
            redis = await get_redis()
            key = self._make_key(user_id, companion_id)

            # 获取现有事实
            facts = await self.get_user_facts(user_id, companion_id)

            # 删除指定事实
            if fact_key in facts:
                del facts[fact_key]

                # 保存回Redis
                if facts:  # 如果还有事实，保存
                    await redis.setex(
                        key,
                        self.expire_seconds,
                        json.dumps(facts, ensure_ascii=False)
                    )
                else:  # 如果没有事实了，删除整个key
                    await redis.delete(key)

                logger.info(f"✅ 删除事实: {fact_key}")
                return True

            logger.warning(f"⚠️ 事实不存在: {fact_key}")
            return False

        except Exception as e:
            logger.error(f"❌ 删除事实失败: {e}")
            return False

    async def clear_user_facts(
        self,
        user_id: str,
        companion_id: int
    ) -> bool:
        """
        清空用户的所有事实

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID

        Returns:
            是否清空成功
        """
        try:
            redis = await get_redis()
            key = self._make_key(user_id, companion_id)

            result = await redis.delete(key)
            if result:
                logger.info(f"✅ 已清空用户事实")
                return True

            logger.warning(f"⚠️ 用户事实已为空")
            return False

        except Exception as e:
            logger.error(f"❌ 清空事实失败: {e}")
            return False

    async def get_fact_categories(
        self,
        user_id: str,
        companion_id: int
    ) -> Dict[str, int]:
        """
        获取用户事实的分类统计

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID

        Returns:
            事实分类统计，例如：
            {
                "基本信息": 3,
                "偏好": 2,
                "梦想": 1
            }
        """
        try:
            facts = await self.get_user_facts(user_id, companion_id)

            # 简单分类规则（可根据key前缀分类）
            categories = {}
            for key in facts.keys():
                if "特殊日期" in key:
                    cat = "特殊日期"
                elif any(x in key for x in ["喜欢", "讨厌", "热爱"]):
                    cat = "偏好"
                elif "梦想" in key:
                    cat = "梦想"
                else:
                    cat = "基本信息"

                categories[cat] = categories.get(cat, 0) + 1

            return categories

        except Exception as e:
            logger.error(f"❌ 获取分类统计失败: {e}")
            return {}

    async def get_facts_summary(
        self,
        user_id: str,
        companion_id: int
    ) -> str:
        """
        获取用户事实的文本摘要（用于Prompt注入）

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID

        Returns:
            格式化的事实摘要文本
        """
        try:
            facts = await self.get_user_facts(user_id, companion_id)

            if not facts:
                return ""

            # 构建摘要文本
            summary_lines = []
            for key, value in facts.items():
                summary_lines.append(f"- {key}: {value}")

            return "\n".join(summary_lines)

        except Exception as e:
            logger.error(f"❌ 生成摘要失败: {e}")
            return ""


# 全局实例
_redis_memory_instance = None


async def get_redis_memory() -> RedisMemorySystem:
    """
    获取Redis内存系统实例（单例模式）

    Returns:
        RedisMemorySystem实例
    """
    global _redis_memory_instance

    if _redis_memory_instance is None:
        _redis_memory_instance = RedisMemorySystem()

    return _redis_memory_instance
