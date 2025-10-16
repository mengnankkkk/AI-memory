"""
数据模型包

导出所有数据库模型供应用使用
"""
from app.models.companion import Companion, Message
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.relationship import (
    CompanionRelationshipState,
    RelationshipHistory,
    EmotionLog
)
from app.models.event import (
    Event,
    UserEventHistory,
    OfflineLifeLog,
    EventTemplate
)
from app.models.gift import UserGiftInventory

__all__ = [
    # 基础模型
    "Companion",
    "Message",
    "User",
    "ChatSession",

    # 关系状态模型
    "CompanionRelationshipState",
    "RelationshipHistory",
    "EmotionLog",

    # 事件系统模型
    "Event",
    "UserEventHistory",
    "OfflineLifeLog",
    "EventTemplate",

    # 礼物系统模型
    "UserGiftInventory",
]
