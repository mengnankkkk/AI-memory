from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Companion(Base):
    """AI伙伴模型"""
    __tablename__ = "companions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    avatar_id = Column(String(50), nullable=False)
    personality_archetype = Column(String(50), nullable=False)
    custom_greeting = Column(Text, nullable=True)
    description = Column(Text, nullable=True)  # 角色描述
    prompt_version = Column(String(10), nullable=True, default="v1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系 - 暂时注释掉避免循环导入问题
    # chat_sessions = relationship("app.models.chat_session.ChatSession", back_populates="companion")


class Message(Base):
    """对话消息模型"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    companion_id = Column(Integer, index=True, nullable=False)
    role = Column(String(20), nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    feedback_score = Column(Integer, nullable=True)  # 1=点赞，-1=点踩
