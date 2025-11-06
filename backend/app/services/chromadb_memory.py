"""
ChromaDB本地向量数据库实现 - L2情景记忆系统

该模块使用ChromaDB实现高效的本地向量存储，用于存储和检索
与用户相关的对话片段和情景记忆。
"""
import logging
import uuid
from typing import List, Dict, Optional
import json

logger = logging.getLogger("chromadb_memory")

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB未安装，情景记忆功能不可用")


class ChromaMemorySystem:
    """
    基于ChromaDB的L2情景记忆系统实现

    特点：
    - 本地存储（无需额外服务）
    - 自动embedding（内置向量化）
    - 支持元数据过滤
    - 开箱即用
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        初始化ChromaDB客户端

        Args:
            persist_directory: 数据持久化目录
        """
        if not CHROMADB_AVAILABLE:
            raise RuntimeError("ChromaDB未安装，请运行 pip install chromadb")

        try:
            # 创建持久化客户端（显式禁用遥测避免 PostHog 阻塞）
            from chromadb.config import Settings
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name="conversation_memories",
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(f"✅ ChromaDB已初始化，数据目录: {persist_directory}")
        except Exception as e:
            logger.error(f"❌ ChromaDB初始化失败: {e}")
            raise

    async def get_recent_memories(
        self,
        user_id: str,
        companion_id: int,
        query: str,
        limit: int = 5
    ) -> List[str]:
        """
        获取与用户查询相关的情景记忆

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            query: 查询文本（通常是用户当前消息）
            limit: 返回的最大记忆条数

        Returns:
            相关记忆文本列表，例如：
            [
                "几天前我们讨论过你的梦想",
                "你曾提到喜欢下雨天",
                ...
            ]
        """
        try:
            if not query or not query.strip():
                logger.warning("查询文本为空，跳过记忆查询")
                return []

            # 使用Where过滤条件查询特定用户和伙伴的记忆
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where={
                    "$and": [
                        {"user_id": user_id},
                        {"companion_id": companion_id}
                    ]
                }
            )

            # 提取记忆文本
            if results and results.get("documents") and results["documents"][0]:
                memories = results["documents"][0]
                logger.info(f"✅ 查询到 {len(memories)} 条相关记忆")
                return memories

            logger.info("📝 未找到相关记忆")
            return []

        except Exception as e:
            logger.error(f"❌ 查询记忆失败: {e}")
            return []

    async def save_memory(
        self,
        user_id: str,
        companion_id: int,
        memory_text: str,
        memory_type: str = "conversation"
    ) -> bool:
        """
        保存新的情景记忆到ChromaDB

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            memory_text: 记忆内容文本
            memory_type: 记忆类型（conversation/event/interaction等）

        Returns:
            是否保存成功
        """
        try:
            if not memory_text or not memory_text.strip():
                logger.warning("记忆文本为空，跳过保存")
                return False

            # 生成唯一ID
            memory_id = str(uuid.uuid4())

            # 添加到集合
            self.collection.add(
                documents=[memory_text],
                metadatas=[{
                    "user_id": user_id,
                    "companion_id": str(companion_id),  # 转为字符串以支持过滤
                    "type": memory_type,
                    "created_at": self._get_timestamp()
                }],
                ids=[memory_id]
            )

            logger.info(f"✅ 记忆已保存 (ID: {memory_id})")
            return True

        except Exception as e:
            logger.error(f"❌ 保存记忆失败: {e}")
            return False

    async def delete_old_memories(
        self,
        user_id: str,
        companion_id: int,
        keep_recent: int = 100
    ) -> int:
        """
        删除过旧的记忆，保持数据库大小可控

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            keep_recent: 保留最近的N条记忆

        Returns:
            删除的记忆条数
        """
        try:
            # 查询该用户的所有记忆
            all_memories = self.collection.get(
                where={
                    "$and": [
                        {"user_id": user_id},
                        {"companion_id": companion_id}
                    ]
                }
            )

            total_count = len(all_memories.get("ids", []))
            delete_count = max(0, total_count - keep_recent)

            if delete_count > 0:
                # 删除最旧的记忆（IDs顺序通常是创建顺序）
                ids_to_delete = all_memories["ids"][:delete_count]
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"✅ 已清理 {delete_count} 条过旧记忆")
                return delete_count

            return 0

        except Exception as e:
            logger.error(f"❌ 清理旧记忆失败: {e}")
            return 0

    async def get_memory_stats(
        self,
        user_id: str,
        companion_id: int
    ) -> Dict:
        """
        获取该用户伙伴对的记忆统计信息

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID

        Returns:
            统计信息字典
        """
        try:
            all_memories = self.collection.get(
                where={
                    "$and": [
                        {"user_id": user_id},
                        {"companion_id": companion_id}
                    ]
                }
            )

            total_count = len(all_memories.get("ids", []))

            # 统计记忆类型
            type_stats = {}
            metadatas = all_memories.get("metadatas", [])
            for meta in metadatas:
                mem_type = meta.get("type", "unknown")
                type_stats[mem_type] = type_stats.get(mem_type, 0) + 1

            return {
                "total_memories": total_count,
                "type_distribution": type_stats,
                "user_id": user_id,
                "companion_id": companion_id
            }

        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return {
                "total_memories": 0,
                "type_distribution": {},
                "error": str(e)
            }

    def _get_timestamp(self) -> str:
        """获取当前ISO格式时间戳"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


# 全局实例（延迟初始化）
_chroma_instance = None


async def get_chroma_memory() -> Optional[ChromaMemorySystem]:
    """
    获取ChromaDB实例（单例模式）

    Returns:
        ChromaMemorySystem实例，如果初始化失败返回None
    """
    global _chroma_instance

    if _chroma_instance is None and CHROMADB_AVAILABLE:
        try:
            _chroma_instance = ChromaMemorySystem()
        except Exception as e:
            logger.error(f"无法初始化ChromaDB: {e}")
            return None

    return _chroma_instance
