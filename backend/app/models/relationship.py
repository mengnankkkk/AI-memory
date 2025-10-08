"""
关系状态数据模型
支持双阶段"心流"交互协议的关系状态管理
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class CompanionRelationshipState(Base):
    """
    伙伴关系状态表

    存储用户与AI伙伴之间的核心关系数据：
    - 好感度系统（affinity）
    - 信任度系统（trust）
    - 紧张度系统（tension）
    - 关系阶段（romance_stage）
    - 情感状态（current_mood）
    """
    __tablename__ = "companion_relationship_states"

    id = Column(Integer, primary_key=True, index=True)

    # 关系标识
    user_id = Column(String(255), nullable=False, index=True)
    companion_id = Column(String(255), nullable=False, index=True)

    # 核心状态指标
    affinity_score = Column(
        Integer,
        nullable=False,
        default=50,
        comment="好感度分数 (0-1000)"
    )
    trust_score = Column(
        Integer,
        nullable=False,
        default=10,
        comment="信任度分数 (0-100)"
    )
    tension_score = Column(
        Integer,
        nullable=False,
        default=0,
        comment="紧张度分数 (0-100)"
    )

    # 关系阶段
    romance_stage = Column(
        String(50),
        nullable=False,
        default='stranger',
        comment="关系阶段: stranger/acquaintance/friend/close_friend/special/romantic/lover"
    )

    # 情感状态
    current_mood = Column(
        String(50),
        nullable=False,
        default='neutral',
        comment="当前心情状态"
    )

    # 特殊标记（存储额外的状态信息）
    special_flags = Column(
        JSON,
        nullable=False,
        default=dict,
        comment="特殊标记和扩展数据"
    )

    # 交互统计
    total_interactions = Column(
        Integer,
        nullable=False,
        default=0,
        comment="总交互次数"
    )

    positive_interactions = Column(
        Integer,
        nullable=False,
        default=0,
        comment="正面交互次数"
    )

    negative_interactions = Column(
        Integer,
        nullable=False,
        default=0,
        comment="负面交互次数"
    )

    # 时间戳
    last_interaction_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="最后交互时间"
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="创建时间"
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 唯一约束
    __table_args__ = (
        {'comment': '伙伴关系状态表 - 存储用户与AI伙伴的关系核心数据'},
    )


class RelationshipHistory(Base):
    """
    关系变化历史表

    记录关系状态的所有重要变化，用于：
    - 关系发展轨迹分析
    - 好感度变化追踪
    - 等级升降记录
    """
    __tablename__ = "relationship_history"

    id = Column(Integer, primary_key=True, index=True)

    # 关系标识
    user_id = Column(String(255), nullable=False, index=True)
    companion_id = Column(String(255), nullable=False, index=True)

    # 变化类型
    change_type = Column(
        String(50),
        nullable=False,
        comment="变化类型: affinity_change/level_change/mood_change等"
    )

    # 变化数据
    old_value = Column(String(100), comment="旧值")
    new_value = Column(String(100), comment="新值")
    delta = Column(Integer, comment="变化量（如适用）")

    # 触发原因
    trigger_reason = Column(
        String(255),
        comment="触发原因"
    )

    trigger_context = Column(
        JSON,
        comment="触发上下文数据"
    )

    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="记录时间"
    )

    __table_args__ = (
        {'comment': '关系变化历史表 - 记录所有重要的关系状态变化'},
    )


class EmotionLog(Base):
    """
    情感日志表

    记录每次交互的情感分析结果，用于：
    - 情感趋势分析
    - 用户行为模式识别
    - 系统优化和调试
    """
    __tablename__ = "emotion_logs"

    id = Column(Integer, primary_key=True, index=True)

    # 关系标识
    user_id = Column(String(255), nullable=False, index=True)
    companion_id = Column(String(255), nullable=False, index=True)

    # 情感分析结果
    primary_emotion = Column(
        String(50),
        nullable=False,
        comment="主要情感类型"
    )

    emotion_intensity = Column(
        Integer,
        nullable=False,
        comment="情感强度 (0-100)"
    )

    detected_emotions = Column(
        JSON,
        comment="检测到的具体情感列表"
    )

    user_intent = Column(
        String(100),
        comment="用户意图"
    )

    # 状态变化
    affinity_change = Column(Integer, default=0, comment="好感度变化")
    trust_change = Column(Integer, default=0, comment="信任度变化")
    tension_change = Column(Integer, default=0, comment="紧张度变化")

    # 是否重要
    is_memorable = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否值得长期记忆"
    )

    is_appropriate = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否适合当前关系"
    )

    # 消息内容摘要
    user_message_summary = Column(
        String(500),
        comment="用户消息摘要"
    )

    ai_response_summary = Column(
        String(500),
        comment="AI回复摘要"
    )

    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="记录时间"
    )

    __table_args__ = (
        {'comment': '情感日志表 - 记录每次交互的情感分析数据'},
    )
