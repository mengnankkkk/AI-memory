"""
记忆系统集成助手 - L1(工作记忆) + L2(ChromaDB情景记忆) + L3(Redis语义记忆)

该模块提供统一的记忆系统接口，按照L1→L2→L3的优先级来处理记忆。

集成流程：
1. L1工作记忆：从内存会话中获取（当前对话上下文）
2. L2情景记忆：从ChromaDB中检索（长期对话片段）
3. L3语义记忆：从Redis中获取（用户事实库）

集成点：
1. response_coordinator.py调用memory_system的方法
2. chat.py在保存消息时使用save_memory
3. 自动事实提取从对话中学习用户信息
"""
from typing import List, Dict, Optional, Tuple
import logging
from app.services.memory_manager import memory_manager  # L1工作记忆
from app.services.chromadb_memory import get_chroma_memory, CHROMADB_AVAILABLE  # L2情景记忆
from app.services.redis_memory import get_redis_memory  # L3语义记忆

logger = logging.getLogger("memory_integration")


class MemorySystemInterface:
    """
    统一记忆系统接口 - L1→L2→L3三层协同

    工作流程：
    - 查询：L1会话→L2向量→L3事实
    - 保存：L1会话→L2存储→L3提取
    """

    async def get_recent_memories(
        self,
        user_id: str,
        companion_id: int,
        query: str,
        limit: int = 5
    ) -> Optional[List[str]]:
        """
        获取相关的情景记忆（L2）

        从ChromaDB向量数据库查询与当前消息相关的历史对话片段

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            query: 查询内容（通常是用户当前消息）
            limit: 返回数量限制

        Returns:
            相关记忆列表或None
        """
        try:
            # 第一步：尝试从L2获取（如果可用）
            if CHROMADB_AVAILABLE:
                chroma = await get_chroma_memory()
                if chroma:
                    memories = await chroma.get_recent_memories(
                        user_id=user_id,
                        companion_id=companion_id,
                        query=query,
                        limit=limit
                    )
                    if memories:
                        logger.info(f"✓ L2查询: 获取 {len(memories)} 条情景记忆")
                        return memories

            logger.debug("L2未获取到记忆，返回None")
            return None

        except Exception as e:
            logger.error(f"L2查询失败: {e}")
            return None

    async def get_user_facts(
        self,
        user_id: str,
        companion_id: int
    ) -> Optional[Dict[str, str]]:
        """
        获取用户的结构化事实（L3）

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID

        Returns:
            用户事实字典或None
        """
        try:
            redis_mem = await get_redis_memory()
            facts = await redis_mem.get_user_facts(user_id, companion_id)

            if facts:
                logger.info(f"✓ L3查询: 获取 {len(facts)} 个用户事实")
                return facts

            return None

        except Exception as e:
            logger.error(f"L3查询失败: {e}")
            return None

    async def save_memory(
        self,
        user_id: str,
        companion_id: int,
        user_message: str,
        ai_response: str,
        session_id: str,
        memory_type: str = "conversation"
    ) -> bool:
        """
        保存新记忆到L2和L3

        流程：
        1. L1: 保存到会话内存（自动处理）
        2. L2: 保存完整对话到ChromaDB
        3. L3: 从对话提取事实到Redis

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            user_message: 用户消息
            ai_response: AI回复
            session_id: 会话ID
            memory_type: 记忆类型

        Returns:
            是否保存成功
        """
        success = True

        # L1: 会话记忆已由chat.py自动处理
        logger.debug("L1: 会话消息已添加到session_memory")

        # L2: 保存到ChromaDB
        if CHROMADB_AVAILABLE:
            try:
                chroma = await get_chroma_memory()
                if chroma:
                    memory_text = f"用户: {user_message}\nAI: {ai_response}"
                    await chroma.save_memory(
                        user_id=user_id,
                        companion_id=companion_id,
                        memory_text=memory_text,
                        memory_type=memory_type
                    )
                    logger.info("✓ L2: 情景记忆已保存")
            except Exception as e:
                logger.warning(f"⚠ L2保存失败: {e}")
                success = False
        else:
            logger.debug("L2: ChromaDB未可用")

        # L3: 自动提取事实
        try:
            redis_mem = await get_redis_memory()
            extracted_facts = await self._extract_facts(
                f"{user_message}\n{ai_response}"
            )
            if extracted_facts:
                await redis_mem.save_multiple_facts(
                    user_id=user_id,
                    companion_id=companion_id,
                    facts=extracted_facts
                )
                logger.info(f"✓ L3: 提取 {len(extracted_facts)} 个新事实")
        except Exception as e:
            logger.warning(f"⚠ L3事实提取失败: {e}")

        return success

    async def extract_and_update_facts(
        self,
        user_id: str,
        companion_id: int,
        conversation_text: str,
        llm_service=None
    ) -> bool:
        """
        从对话中提取用户事实并更新L3

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            conversation_text: 对话内容
            llm_service: LLM服务实例（用于事实提取）

        Returns:
            是否提取成功
        """
        try:
            extracted_facts = await self._extract_facts(conversation_text, llm_service)

            if extracted_facts:
                redis_mem = await get_redis_memory()
                success = await redis_mem.save_multiple_facts(
                    user_id=user_id,
                    companion_id=companion_id,
                    facts=extracted_facts
                )
                logger.info(f"✓ L3: 更新了 {len(extracted_facts)} 个事实")
                return success

            return False

        except Exception as e:
            logger.error(f"L3事实提取失败: {e}")
            return False

    async def get_memory_summary(
        self,
        user_id: str,
        companion_id: int
    ) -> Dict:
        """
        获取记忆系统的完整摘要（L2+L3）

        Returns:
            包含L2和L3统计的摘要字典
        """
        summary = {
            "l2_episodic": None,
            "l3_semantic": None,
            "combined_summary": ""
        }

        try:
            # L2统计
            if CHROMADB_AVAILABLE:
                chroma = await get_chroma_memory()
                if chroma:
                    summary["l2_episodic"] = await chroma.get_memory_stats(
                        user_id, companion_id
                    )

            # L3统计
            redis_mem = await get_redis_memory()
            facts = await redis_mem.get_user_facts(user_id, companion_id)
            if facts:
                summary["l3_semantic"] = {
                    "total_facts": len(facts),
                    "facts": facts
                }

            # 组合摘要
            summaries = []
            if summary["l2_episodic"]:
                summaries.append(
                    f"L2: {summary['l2_episodic'].get('total_memories', 0)} 条对话记忆"
                )
            if summary["l3_semantic"]:
                summaries.append(
                    f"L3: {summary['l3_semantic']['total_facts']} 个用户事实"
                )

            summary["combined_summary"] = " | ".join(summaries) if summaries else "暂无长期记忆"

            return summary

        except Exception as e:
            logger.error(f"摘要获取失败: {e}")
            return summary

    async def _extract_facts(
        self,
        text: str,
        llm_service=None
    ) -> Optional[Dict[str, str]]:
        """
        使用LLM从文本中提取结构化事实

        Args:
            text: 输入文本
            llm_service: LLM服务实例

        Returns:
            提取的事实字典
        """
        try:
            if not llm_service:
                from app.services.llm.factory import llm_service as default_llm
                llm_service = default_llm

            # 构建提示词
            prompt = f"""从以下文本中提取关于用户的事实信息。
只提取明确提到的信息，不要推断。
以JSON格式返回，键为事实类型，值为具体内容。

示例：{{"昵称": "小星", "职业": "画家"}}

文本：
{text}

请只返回JSON对象，不要包含其他文本。"""

            # 调用LLM
            response = await llm_service.chat_completion([
                {"role": "user", "content": prompt}
            ])

            # 解析JSON
            import json
            facts = json.loads(response)

            if facts:
                logger.debug(f"提取 {len(facts)} 个事实")
                return facts
            return None

        except json.JSONDecodeError:
            logger.debug("LLM返回非JSON格式，跳过事实提取")
            return None
        except Exception as e:
            logger.warning(f"事实提取异常: {e}")
            return None


# 全局记忆系统实例
memory_system = MemorySystemInterface()

logger.info("✓ 记忆系统已初始化 (L1→L2→L3)")


# ============================================================
# 如何在chat.py中使用
# ============================================================

"""
在 chat.py 的 chat() 函数中，替换以下代码：

    # 旧代码：
    recent_memories = None
    user_facts = None

    # 新代码：
    from app.services.memory_integration import memory_system

    recent_memories = await memory_system.get_recent_memories(
        user_id=companion.user_id,
        companion_id=request.companion_id,
        query=request.message,
        limit=5
    )

    user_facts = await memory_system.get_user_facts(
        user_id=companion.user_id,
        companion_id=request.companion_id
    )

这样AffinityEngine就能自动在生成的Prompt中融合记忆系统！
"""


# ============================================================
# 记忆系统实现示例（使用Redis + 简化版）
# ============================================================

class SimpleRedisMemorySystem(MemorySystemInterface):
    """
    简化版记忆系统实现示例

    使用Redis存储，适合快速原型
    生产环境建议使用专业向量数据库
    """

    def __init__(self, redis_client):
        self.redis = redis_client

    async def get_user_facts(
        self,
        user_id: str,
        companion_id: int
    ) -> Dict[str, str]:
        """从Redis获取用户事实"""
        key = f"user_facts:{user_id}:{companion_id}"
        try:
            facts_json = await self.redis.get(key)
            if facts_json:
                import json
                return json.loads(facts_json)
        except Exception as e:
            logger.error(f"获取用户事实失败: {e}")
        return {}

    async def save_user_fact(
        self,
        user_id: str,
        companion_id: int,
        fact_key: str,
        fact_value: str
    ):
        """保存单个用户事实"""
        key = f"user_facts:{user_id}:{companion_id}"
        try:
            facts = await self.get_user_facts(user_id, companion_id)
            facts[fact_key] = fact_value

            import json
            await self.redis.set(key, json.dumps(facts, ensure_ascii=False))
            logger.info(f"保存用户事实: {fact_key} = {fact_value}")
        except Exception as e:
            logger.error(f"保存用户事实失败: {e}")


# ============================================================
# 使用专业向量数据库的示例代码
# ============================================================

"""
# 方案1: 使用Pinecone

from pinecone import Pinecone

class PineconeMemorySystem(MemorySystemInterface):
    def __init__(self, api_key: str, index_name: str):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)

    async def get_recent_memories(self, user_id, companion_id, query, limit=5):
        # 1. 对query进行embedding
        query_embedding = await self.get_embedding(query)

        # 2. 向量搜索
        results = self.index.query(
            vector=query_embedding,
            filter={
                "user_id": user_id,
                "companion_id": companion_id
            },
            top_k=limit,
            include_metadata=True
        )

        # 3. 返回记忆文本
        return [match['metadata']['text'] for match in results['matches']]


# 方案2: 使用Milvus

from pymilvus import connections, Collection

class MilvusMemorySystem(MemorySystemInterface):
    def __init__(self, host: str, collection_name: str):
        connections.connect(host=host, port="19530")
        self.collection = Collection(collection_name)

    async def get_recent_memories(self, user_id, companion_id, query, limit=5):
        query_embedding = await self.get_embedding(query)

        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            expr=f'user_id == "{user_id}" && companion_id == {companion_id}'
        )

        return [hit.entity.get('memory_text') for hit in results[0]]


# 方案3: 使用ChromaDB (本地向量数据库)

import chromadb

class ChromaMemorySystem(MemorySystemInterface):
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="conversation_memories"
        )

    async def get_recent_memories(self, user_id, companion_id, query, limit=5):
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where={
                "user_id": user_id,
                "companion_id": companion_id
            }
        )

        return results['documents'][0] if results['documents'] else []

    async def save_memory(self, user_id, companion_id, memory_text, memory_type="conversation"):
        import uuid
        self.collection.add(
            documents=[memory_text],
            metadatas=[{
                "user_id": user_id,
                "companion_id": companion_id,
                "type": memory_type
            }],
            ids=[str(uuid.uuid4())]
        )
"""
