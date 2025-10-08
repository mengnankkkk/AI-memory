"""
事件系统数据模型
支持动态事件触发和剧情发展
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Event(Base):
    """
    事件定义表

    存储所有可触发的事件定义：
    - 主线事件（MAIN）
    - 随机事件（RANDOM）
    - 日期事件（DATE）
    - 特殊事件（SPECIAL）
    """
    __tablename__ = "events"

    # 主键
    event_id = Column(Integer, primary_key=True, index=True)

    # 事件标识
    event_code = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="事件唯一编码"
    )

    event_name = Column(
        String(255),
        nullable=False,
        comment="事件名称"
    )

    # 事件类型
    event_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="事件类型: MAIN/RANDOM/DATE/SPECIAL"
    )

    # 事件分类
    category = Column(
        String(50),
        comment="事件分类: romance/friendship/conflict/milestone等"
    )

    # 触发条件
    trigger_conditions = Column(
        JSON,
        nullable=False,
        comment="触发条件JSON配置"
    )

    # 是否可重复触发
    is_repeatable = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否可重复触发"
    )

    # 冷却时间（小时）
    cooldown_hours = Column(
        Integer,
        default=0,
        comment="重复触发冷却时间（小时）"
    )

    # 事件脚本内容
    script_content = Column(
        JSON,
        nullable=False,
        comment="事件脚本内容JSON"
    )

    # 事件影响
    effects = Column(
        JSON,
        comment="事件影响配置（好感度、信任度等）"
    )

    # 优先级
    priority = Column(
        Integer,
        default=0,
        comment="事件优先级（数字越大优先级越高）"
    )

    # 启用状态
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否启用"
    )

    # 事件描述
    description = Column(
        Text,
        comment="事件描述"
    )

    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    __table_args__ = (
        {'comment': '事件定义表 - 存储所有可触发事件的配置'},
    )


class UserEventHistory(Base):
    """
    用户事件历史表

    记录用户触发的所有事件：
    - 事件触发时间
    - 用户选择
    - 事件结果
    """
    __tablename__ = "user_event_history"

    id = Column(Integer, primary_key=True, index=True)

    # 用户标识
    user_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="用户ID"
    )

    companion_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="伙伴ID"
    )

    # 事件信息
    event_id = Column(
        Integer,
        ForeignKey("events.event_id"),
        nullable=False,
        index=True,
        comment="事件ID"
    )

    event_code = Column(
        String(100),
        nullable=False,
        comment="事件编码（冗余字段，便于查询）"
    )

    # 用户选择
    choice_made = Column(
        String(10),
        comment="用户做出的选择（如A/B/C）"
    )

    choice_content = Column(
        String(500),
        comment="选择内容文本"
    )

    # 事件结果
    result_data = Column(
        JSON,
        comment="事件结果数据"
    )

    # 状态影响
    affinity_delta = Column(
        Integer,
        default=0,
        comment="好感度变化"
    )

    trust_delta = Column(
        Integer,
        default=0,
        comment="信任度变化"
    )

    tension_delta = Column(
        Integer,
        default=0,
        comment="紧张度变化"
    )

    # 完成状态
    is_completed = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否已完成"
    )

    # 时间戳
    triggered_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="触发时间"
    )

    completed_at = Column(
        DateTime(timezone=True),
        comment="完成时间"
    )

    # 关系
    event = relationship("Event", foreign_keys=[event_id])

    __table_args__ = (
        {'comment': '用户事件历史表 - 记录用户触发的所有事件'},
    )


class OfflineLifeLog(Base):
    """
    离线生活日志表

    AI伙伴的"离线生活"记录：
    - 模拟AI伙伴在用户离线时的活动
    - 生成有趣的日常生活片段
    - 增强角色真实感
    """
    __tablename__ = "offline_life_logs"

    id = Column(Integer, primary_key=True, index=True)

    # 伙伴标识
    companion_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="伙伴ID"
    )

    # 日志内容
    log_content = Column(
        Text,
        nullable=False,
        comment="日志内容"
    )

    # 日志类型
    log_type = Column(
        String(50),
        comment="日志类型: daily_life/thinking/learning/activity等"
    )

    # 重要性分数
    importance_score = Column(
        Integer,
        nullable=False,
        default=50,
        comment="重要性分数 (0-100)"
    )

    # 关联的情感
    associated_emotion = Column(
        String(50),
        comment="关联的情感"
    )

    # 是否已分享给用户
    is_shared_with_user = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否已分享给用户"
    )

    # 分享时间
    shared_at = Column(
        DateTime(timezone=True),
        comment="分享时间"
    )

    # 用户反馈
    user_reaction = Column(
        String(50),
        comment="用户反应"
    )

    # 时间戳
    generated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="生成时间"
    )

    __table_args__ = (
        {'comment': '离线生活日志表 - AI伙伴的离线活动记录'},
    )


class EventTemplate(Base):
    """
    事件模板表

    存储事件脚本的可重用模板
    """
    __tablename__ = "event_templates"

    id = Column(Integer, primary_key=True, index=True)

    # 模板信息
    template_name = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="模板名称"
    )

    template_type = Column(
        String(50),
        nullable=False,
        comment="模板类型"
    )

    # 模板内容
    template_content = Column(
        JSON,
        nullable=False,
        comment="模板内容JSON"
    )

    # 模板变量
    required_variables = Column(
        JSON,
        comment="必需变量列表"
    )

    # 描述
    description = Column(
        Text,
        comment="模板描述"
    )

    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    __table_args__ = (
        {'comment': '事件模板表 - 存储可重用的事件脚本模板'},
    )
