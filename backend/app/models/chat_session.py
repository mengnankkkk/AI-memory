"""
聊天会话模型
用于管理用户与AI伙伴的对话历史
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class ChatSession(Base):
    """聊天会话表"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)  # 用户ID
    companion_id = Column(Integer, ForeignKey("companions.id"), nullable=False)  # 关联的AI伙伴
    session_title = Column(String(200), nullable=True)  # 会话标题（自动生成或用户自定义）
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 最后更新时间
    is_active = Column(Boolean, default=True)  # 是否活跃
    total_messages = Column(Integer, default=0)  # 消息总数
    
    # 关联关系 - 暂时注释掉避免循环导入问题
    # companion = relationship("app.models.companion.Companion", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """聊天消息表"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)  # 关联的会话
    role = Column(String(20), nullable=False)  # 角色：user/assistant/system
    content = Column(Text, nullable=False)  # 消息内容
    timestamp = Column(DateTime, default=datetime.utcnow)  # 发送时间
    tokens_used = Column(Integer, default=0)  # 使用的token数量（可选）
    
    # 关联关系
    session = relationship("ChatSession", back_populates="messages")
