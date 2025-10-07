"""
记忆系统集成助手

如果你有三层记忆系统(L1工作记忆、L2情景记忆、L3语义记忆)，
本模块提供了与AffinityEngine集成的接口
"""
from typing import List, Dict, Optional
import logging

logger = logging.getLogger("memory_integration")


class MemorySystemInterface:
    """
    记忆系统接口

    如果你已经实现了记忆系统，请实现这个接口的方法
    然后在chat.py中调用
    """

    async def get_recent_memories(
        self,
        user_id: str,
        companion_id: int,
        query: str,
        limit: int = 5
    ) -> List[str]:
        """
        获取相关的情景记忆 (L2)

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            query: 查询内容(用户当前消息)
            limit: 返回数量限制

        Returns:
            相关记忆列表，例如：
            [
                "几天前，我们在雨天聊过热可可的话题，用户很体贴。",
                "用户提到过TA的梦想是成为一名画家。",
                ...
            ]

        实现建议：
        1. 使用向量数据库(如Pinecone、Milvus)存储对话记忆
        2. 对query进行embedding
        3. 执行相似度搜索
        4. 返回最相关的记忆片段
        """
        # TODO: 实现你的L2情景记忆查询逻辑
        logger.warning("[Memory] L2情景记忆未实现，返回空列表")
        return []

    async def get_user_facts(
        self,
        user_id: str,
        companion_id: int
    ) -> Dict[str, str]:
        """
        获取关于用户的语义事实 (L3)

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

        实现建议：
        1. 使用KV数据库(如Redis、DynamoDB)存储用户事实
        2. 键名格式: user_facts:{user_id}:{companion_id}
        3. 自动从对话中提取并更新事实
        """
        # TODO: 实现你的L3语义记忆查询逻辑
        logger.warning("[Memory] L3语义记忆未实现，返回空字典")
        return {}

    async def save_memory(
        self,
        user_id: str,
        companion_id: int,
        memory_text: str,
        memory_type: str = "conversation"
    ):
        """
        保存新记忆到L2

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            memory_text: 记忆内容
            memory_type: 记忆类型
        """
        # TODO: 实现保存记忆到向量数据库
        logger.warning("[Memory] 记忆保存功能未实现")
        pass

    async def extract_and_update_facts(
        self,
        user_id: str,
        companion_id: int,
        conversation_text: str,
        llm_service
    ):
        """
        从对话中提取用户事实并更新L3

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            conversation_text: 对话内容
            llm_service: LLM服务实例

        实现建议：
        使用LLM提取结构化信息：
        ```
        Prompt: "从以下对话中提取关于用户的事实信息，以JSON格式返回。
        对话：{conversation_text}
        JSON格式：{\"昵称\": \"...\", \"喜欢的颜色\": \"...\", ...}"
        ```
        """
        # TODO: 实现从对话提取事实
        logger.warning("[Memory] 事实提取功能未实现")
        pass


# 全局记忆系统实例
memory_system = MemorySystemInterface()


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
