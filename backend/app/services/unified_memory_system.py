"""
统一记忆系统 - 整合L2(ChromaDB)和L3(Redis)

该模块提供一个统一的接口，同时利用ChromaDB的情景记忆
和Redis的语义记忆，提供完整的长期记忆能力。
"""
import logging
from typing import List, Dict, Optional, Tuple
from app.services.chromadb_memory import get_chroma_memory, CHROMADB_AVAILABLE
from app.services.redis_memory import get_redis_memory
from app.services.llm.factory import llm_service

logger = logging.getLogger("unified_memory_system")


class UnifiedMemorySystem:
    """
    统一记忆系统

    同时支持：
    - L2情景记忆 (ChromaDB): 对话片段、关键事件
    - L3语义记忆 (Redis): 结构化用户事实

    协同工作流程：
    1. 查询时：先从L3获取用户事实作为上下文，再从L2检索相关情景
    2. 保存时：提取LLM分析的事实到L3，完整对话存储到L2
    """

    def __init__(self):
        """初始化统一记忆系统"""
        self.chroma_ready = CHROMADB_AVAILABLE
        logger.info(f"📚 统一记忆系统已初始化 (ChromaDB支持: {self.chroma_ready})")

    async def get_recent_memories(
        self,
        user_id: str,
        companion_id: int,
        query: str,
        limit: int = 5
    ) -> Optional[List[str]]:
        """
        获取相关的情景记忆 (L2)

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            query: 查询文本
            limit: 返回的最大记忆条数

        Returns:
            相关记忆列表，如果未启用L2返回None
        """
        if not self.chroma_ready:
            logger.debug("⚠️ ChromaDB未可用，跳过L2查询")
            return None

        try:
            chroma = await get_chroma_memory()
            if not chroma:
                return None

            memories = await chroma.get_recent_memories(
                user_id=user_id,
                companion_id=companion_id,
                query=query,
                limit=limit
            )

            return memories if memories else None

        except Exception as e:
            logger.warning(f"❌ L2情景记忆查询失败: {e}")
            return None

    async def get_user_facts(
        self,
        user_id: str,
        companion_id: int
    ) -> Optional[Dict[str, str]]:
        """
        获取用户的结构化事实 (L3)

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID

        Returns:
            用户事实字典，如果无事实返回None
        """
        try:
            redis_mem = await get_redis_memory()
            facts = await redis_mem.get_user_facts(user_id, companion_id)

            return facts if facts else None

        except Exception as e:
            logger.warning(f"❌ L3语义记忆查询失败: {e}")
            return None

    async def save_memory(
        self,
        user_id: str,
        companion_id: int,
        memory_text: str,
        memory_type: str = "conversation",
        llm_service_instance=None
    ) -> bool:
        """
        保存新记忆到L2和L3

        流程：
        1. 保存完整对话到L2 (ChromaDB)
        2. 使用LLM从对话提取结构化事实到L3 (Redis)

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            memory_text: 记忆内容
            memory_type: 记忆类型
            llm_service_instance: LLM服务（用于事实提取）

        Returns:
            是否保存成功
        """
        success = True

        # 第一步：保存到L2
        if self.chroma_ready:
            try:
                chroma = await get_chroma_memory()
                if chroma:
                    await chroma.save_memory(
                        user_id=user_id,
                        companion_id=companion_id,
                        memory_text=memory_text,
                        memory_type=memory_type
                    )
            except Exception as e:
                logger.warning(f"⚠️ L2保存失败: {e}")
                success = False
        else:
            logger.debug("⚠️ ChromaDB未可用，跳过L2保存")

        # 第二步：从对话提取事实并保存到L3
        try:
            extracted_facts = await self._extract_facts_from_text(
                memory_text,
                llm_service_instance
            )

            if extracted_facts:
                redis_mem = await get_redis_memory()
                await redis_mem.save_multiple_facts(
                    user_id=user_id,
                    companion_id=companion_id,
                    facts=extracted_facts
                )
        except Exception as e:
            logger.warning(f"⚠️ L3事实提取失败: {e}")
            success = False

        return success

    async def extract_and_update_facts(
        self,
        user_id: str,
        companion_id: int,
        conversation_text: str,
        llm_service_instance=None
    ) -> bool:
        """
        从对话中提取并更新用户事实 (L3)

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            conversation_text: 对话文本
            llm_service_instance: LLM服务

        Returns:
            是否提取成功
        """
        try:
            # 使用LLM提取事实
            extracted_facts = await self._extract_facts_from_text(
                conversation_text,
                llm_service_instance
            )

            if extracted_facts:
                redis_mem = await get_redis_memory()
                success = await redis_mem.save_multiple_facts(
                    user_id=user_id,
                    companion_id=companion_id,
                    facts=extracted_facts
                )
                return success

            return False

        except Exception as e:
            logger.error(f"❌ 事实提取失败: {e}")
            return False

    async def get_memory_summary(
        self,
        user_id: str,
        companion_id: int
    ) -> Dict:
        """
        获取记忆系统的完整摘要

        Returns:
            包含L2和L3的统计信息和摘要
        """
        summary = {
            "l2_episodic": None,
            "l3_semantic": None,
            "combined_summary": ""
        }

        try:
            # L2统计
            if self.chroma_ready:
                chroma = await get_chroma_memory()
                if chroma:
                    summary["l2_episodic"] = await chroma.get_memory_stats(
                        user_id, companion_id
                    )

            # L3统计和摘要
            redis_mem = await get_redis_memory()
            facts = await redis_mem.get_user_facts(user_id, companion_id)
            if facts:
                summary["l3_semantic"] = {
                    "total_facts": len(facts),
                    "categories": await redis_mem.get_fact_categories(
                        user_id, companion_id
                    ),
                    "facts": facts
                }

            # 组合摘要
            summaries = []
            if summary["l2_episodic"]:
                summaries.append(
                    f"有 {summary['l2_episodic'].get('total_memories', 0)} 条对话记忆"
                )
            if summary["l3_semantic"]:
                summaries.append(
                    f"已记录 {summary['l3_semantic']['total_facts']} 个用户事实"
                )

            summary["combined_summary"] = "；".join(summaries) if summaries else "暂无记忆"

            return summary

        except Exception as e:
            logger.error(f"❌ 获取摘要失败: {e}")
            return summary

    async def _extract_facts_from_text(
        self,
        text: str,
        llm_service_instance=None
    ) -> Optional[Dict[str, str]]:
        """
        使用LLM从文本中提取结构化事实

        Args:
            text: 输入文本
            llm_service_instance: LLM服务实例

        Returns:
            提取的事实字典
        """
        try:
            # 使用全局LLM服务或传入的实例
            llm = llm_service_instance or llm_service

            # 构建提示词
            prompt = f"""从以下文本中提取关于用户的事实信息。
只提取明确提到的信息，不要推断。
以JSON格式返回，键为事实类型，值为具体内容。

示例响应：
{{"昵称": "小星", "职业": "画家", "梦想": "举办个人画展"}}

文本：
{text}

请只返回JSON，不要包含其他文本。"""

            # 调用LLM
            response = await llm.chat_completion([
                {"role": "user", "content": prompt}
            ])

            # 解析JSON
            import json
            facts = json.loads(response)

            logger.info(f"✅ 提取 {len(facts)} 个事实")
            return facts

        except json.JSONDecodeError:
            logger.debug("⚠️ LLM返回的非JSON格式，跳过事实提取")
            return None
        except Exception as e:
            logger.warning(f"⚠️ 事实提取失败: {e}")
            return None

    async def get_memory_context_for_prompt(
        self,
        user_id: str,
        companion_id: int,
        query: str = None
    ) -> str:
        """
        获取格式化的记忆上下文，用于注入到系统提示词

        Returns:
            格式化的记忆文本
        """
        context_parts = []

        # 获取L3事实摘要
        try:
            redis_mem = await get_redis_memory()
            facts_summary = await redis_mem.get_facts_summary(
                user_id, companion_id
            )
            if facts_summary:
                context_parts.append("# 关于用户的已知信息\n" + facts_summary)
        except Exception as e:
            logger.warning(f"⚠️ 获取L3摘要失败: {e}")

        # 获取L2记忆（如果有查询）
        if query and self.chroma_ready:
            try:
                memories = await self.get_recent_memories(
                    user_id, companion_id, query, limit=3
                )
                if memories:
                    mem_text = "\n".join([f"- {m}" for m in memories])
                    context_parts.append("# 我们的共同记忆\n" + mem_text)
            except Exception as e:
                logger.warning(f"⚠️ 获取L2记忆失败: {e}")

        return "\n\n".join(context_parts) if context_parts else ""


# 全局统一实例
_unified_memory_system = None


async def get_unified_memory_system() -> UnifiedMemorySystem:
    """
    获取统一记忆系统实例（单例模式）

    Returns:
        UnifiedMemorySystem实例
    """
    global _unified_memory_system

    if _unified_memory_system is None:
        _unified_memory_system = UnifiedMemorySystem()

    return _unified_memory_system
