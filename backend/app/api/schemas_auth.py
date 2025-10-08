"""
认证相关的数据模型
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """用户注册"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class CompanionCreate(BaseModel):
    """创建伙伴"""
    name: str = Field(..., min_length=1, max_length=100)
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
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
