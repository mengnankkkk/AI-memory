from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.companion import Companion, Message
from app.api.schemas import ChatRequest, ChatResponse
from app.services.llm.factory import llm_service  # 使用统一的LLM服务工厂
from app.core.prompts import get_system_prompt
from app.core.config import settings
from typing import List, Dict

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 简单的内存会话存储 (生产环境应使用Redis)
session_memory: Dict[str, List[Dict[str, str]]] = {}


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """处理聊天请求"""
    # 1. 获取伙伴信息
    result = await db.execute(
        select(Companion).where(Companion.id == request.companion_id)
    )
    companion = result.scalar_one_or_none()

    if not companion:
        raise HTTPException(status_code=404, detail="伙伴不存在")

    # 2. 获取系统提示词
    system_prompt = get_system_prompt(
        companion.personality_archetype,
        companion.name
    )

    # 3. 获取会话上下文
    session_key = f"{request.companion_id}:{request.session_id}"
    if session_key not in session_memory:
        session_memory[session_key] = []

    context = session_memory[session_key]

    # 4. 添加用户消息到上下文
    context.append({
        "role": "user",
        "content": request.message
    })

    # 5. 构建完整消息列表
    messages = [
        {"role": "system", "content": system_prompt}
    ] + context[-settings.MAX_CONTEXT_MESSAGES:]

    # 6. 调用LLM服务
    response = await llm_service.chat_completion(messages)

    # 7. 添加助手回复到上下文
    context.append({
        "role": "assistant",
        "content": response
    })

    # 8. 保存消息到数据库
    user_msg = Message(
        companion_id=request.companion_id,
        role="user",
        content=request.message
    )
    assistant_msg = Message(
        companion_id=request.companion_id,
        role="assistant",
        content=response
    )

    db.add(user_msg)
    db.add(assistant_msg)
    await db.commit()

    return ChatResponse(
        message=response,
        companion_name=companion.name
    )


@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """清除会话"""
    keys_to_delete = [key for key in session_memory.keys() if session_id in key]
    for key in keys_to_delete:
        del session_memory[key]

    return {"message": "会话已清除"}
