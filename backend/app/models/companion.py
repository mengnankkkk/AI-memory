from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Companion(Base):
    """AI伙伴模型"""
    __tablename__ = "companions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    avatar_id = Column(String(50), nullable=False)
    personality_archetype = Column(String(50), nullable=False)
    custom_greeting = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Message(Base):
    """对话消息模型"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    companion_id = Column(Integer, index=True, nullable=False)
    role = Column(String(20), nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
