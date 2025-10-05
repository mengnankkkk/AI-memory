from pydantic import BaseModel
from typing import Optional, List


class CompanionCreate(BaseModel):
    """创建伙伴请求"""
    user_id: str
    name: str
    avatar_id: str
    personality_archetype: str
    custom_greeting: Optional[str] = None


class CompanionResponse(BaseModel):
    """伙伴响应"""
    id: int
    user_id: str
    name: str
    avatar_id: str
    personality_archetype: str
    custom_greeting: Optional[str]
    greeting: str  # 生成的问候语

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # user | assistant
    content: str


class ChatRequest(BaseModel):
    """聊天请求"""
    companion_id: int
    message: str
    session_id: str


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str
    companion_name: str
