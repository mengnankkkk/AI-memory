"""
聊天会话相关的API模式
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatSessionCreate(BaseModel):
    """创建会话请求"""
    companion_id: int
    user_id: str
    session_title: Optional[str] = None

class ChatSessionResponse(BaseModel):
    """会话响应"""
    id: int
    user_id: str
    companion_id: int
    session_title: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    total_messages: int
    
    class Config:
        from_attributes = True

class ChatMessageCreate(BaseModel):
    """创建消息请求"""
    content: str
    role: str = "user"

class ChatMessageResponse(BaseModel):
    """消息响应"""
    id: int
    session_id: int
    role: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    """聊天历史响应"""
    session: ChatSessionResponse
    messages: List[ChatMessageResponse]

class UserCompanionsResponse(BaseModel):
    """用户伙伴列表响应"""
    companions: List[dict]
    total: int
