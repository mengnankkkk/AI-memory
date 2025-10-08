"""
聊天会话管理API
支持用户隔离和历史会话管理
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.companion import Companion
from app.models.chat_session import ChatSession, ChatMessage
from app.api.schemas_chat import (
    ChatSessionCreate, ChatSessionResponse, 
    ChatMessageCreate, ChatMessageResponse,
    ChatHistoryResponse, UserCompanionsResponse
)
from typing import List, Optional

router = APIRouter(prefix="/sessions", tags=["chat-sessions"])

@router.get("/companions/{user_id}", response_model=UserCompanionsResponse)
async def get_user_companions(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取用户的所有AI伙伴"""
    try:
        # 查询用户的伙伴，包含会话统计
        stmt = select(Companion).where(Companion.user_id == int(user_id))  # 转换为整数
        result = await db.execute(stmt)
        companions = result.scalars().all()
        
        companions_data = []
        for companion in companions:
            # 统计每个伙伴的会话数
            session_count_stmt = select(ChatSession).where(
                and_(ChatSession.companion_id == companion.id, ChatSession.is_active == True)
            )
            session_result = await db.execute(session_count_stmt)
            session_count = len(session_result.scalars().all())
            
            companions_data.append({
                "id": companion.id,
                "name": companion.name,
                "avatar_id": companion.avatar_id,
                "personality_archetype": companion.personality_archetype,
                "custom_greeting": companion.custom_greeting,
                "created_at": companion.created_at,
                "session_count": session_count
            })
        
        return UserCompanionsResponse(
            companions=companions_data,
            total=len(companions_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取伙伴列表失败: {str(e)}")

@router.post("/", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新的聊天会话"""
    try:
        # 验证伙伴是否存在（允许系统预设伙伴）
        companion_stmt = select(Companion).where(
            Companion.id == session_data.companion_id
        )
        companion_result = await db.execute(companion_stmt)
        companion = companion_result.scalar_one_or_none()
        
        if not companion:
            raise HTTPException(status_code=404, detail="AI伙伴不存在")
        
        # 检查权限：要么是用户自己的伙伴，要么是系统预设伙伴
        if companion.user_id != session_data.user_id and companion.user_id != 1:
            raise HTTPException(status_code=403, detail="无权访问该AI伙伴")
        
        # 创建会话
        session = ChatSession(
            user_id=session_data.user_id,
            companion_id=session_data.companion_id,
            session_title=session_data.session_title or f"与{companion.name}的对话"
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")

@router.get("/{user_id}/history", response_model=List[ChatSessionResponse])
async def get_user_chat_sessions(
    user_id: str,
    companion_id: Optional[int] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取用户的聊天会话历史"""
    try:
        stmt = select(ChatSession).where(
            and_(ChatSession.user_id == int(user_id), ChatSession.is_active == True)  # 转换为整数
        )
        
        if companion_id:
            stmt = stmt.where(ChatSession.companion_id == companion_id)
        
        stmt = stmt.order_by(desc(ChatSession.updated_at)).limit(limit)
        
        result = await db.execute(stmt)
        sessions = result.scalars().all()
        
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话历史失败: {str(e)}")

@router.get("/{session_id}/messages", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取特定会话的完整聊天历史"""
    try:
        # 验证会话是否属于该用户
        stmt = select(ChatSession).options(
            selectinload(ChatSession.messages)
        ).where(
            and_(
                ChatSession.id == session_id,
                ChatSession.user_id == int(user_id)  # 转换为整数
            )
        )
        
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在或不属于该用户")
        
        # 按时间排序消息
        messages = sorted(session.messages, key=lambda x: x.timestamp)
        
        return ChatHistoryResponse(
            session=session,
            messages=messages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取聊天历史失败: {str(e)}")

@router.post("/{session_id}/messages", response_model=ChatMessageResponse)
async def add_message_to_session(
    session_id: int,
    message_data: ChatMessageCreate,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """向会话添加消息"""
    try:
        # 验证会话是否属于该用户
        session_stmt = select(ChatSession).where(
            and_(
                ChatSession.id == session_id,
                ChatSession.user_id == int(user_id),  # 转换为整数
                ChatSession.is_active == True
            )
        )
        
        session_result = await db.execute(session_stmt)
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在或不属于该用户")
        
        # 创建消息
        message = ChatMessage(
            session_id=session_id,
            role=message_data.role,
            content=message_data.content
        )
        
        db.add(message)
        
        # 更新会话统计
        session.total_messages += 1
        session.updated_at = message.timestamp
        
        await db.commit()
        await db.refresh(message)
        
        return message
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加消息失败: {str(e)}")

@router.delete("/{session_id}")
async def delete_chat_session(
    session_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """删除聊天会话（软删除）"""
    try:
        # 验证会话是否属于该用户
        stmt = select(ChatSession).where(
            and_(
                ChatSession.id == session_id,
                ChatSession.user_id == int(user_id)  # 转换为整数
            )
        )
        
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在或不属于该用户")
        
        # 软删除（设置为非活跃状态）
        session.is_active = False
        await db.commit()
        
        return {"message": "会话已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除会话失败: {str(e)}")
