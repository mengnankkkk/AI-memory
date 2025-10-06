from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.companion import Companion, Message
from app.api.schemas import ChatRequest, ChatResponse
from app.services.llm.factory import llm_service  # 使用统一的LLM服务工厂
from app.core.prompts import get_prompt_by_version
from app.core.config import settings
from typing import List, Dict
from app.services.llm.dedup_cache import get_llm_cache_key, get_cached_llm_response, set_cached_llm_response
from app.services.analytics import analytics_service
from app.services.hot_cache import hot_conversation_cache

router = APIRouter(prefix="/chat", tags=["chat"])

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

    # 2. 获取系统提示词，优先用自定义，其次用指定版本Prompt
    prompt_version = getattr(companion, 'prompt_version', 'v1')
    if companion.custom_greeting:
        system_prompt = companion.custom_greeting
    else:
        system_prompt = get_prompt_by_version(prompt_version, companion.name, companion.personality_archetype)

    # 埋点：记录Prompt使用
    await analytics_service.track_prompt_usage(
        companion.user_id, request.companion_id, prompt_version, companion.personality_archetype
    )

    # 3. 检查热门对话缓存
    hot_response = await hot_conversation_cache.get_cached_response(
        companion.personality_archetype, request.message
    )
    if hot_response:
        # 直接返回缓存的热门回复
        # 仍需保存到数据库
        user_msg = Message(
            companion_id=request.companion_id,
            role="user",
            content=request.message
        )
        assistant_msg = Message(
            companion_id=request.companion_id,
            role="assistant",
            content=hot_response
        )
        db.add(user_msg)
        db.add(assistant_msg)
        await db.commit()
        return ChatResponse(
            message=hot_response,
            companion_name=companion.name
        )

    # 4. 获取会话上下文
    session_key = f"{request.companion_id}:{request.session_id}"
    if session_key not in session_memory:
        session_memory[session_key] = []
    context = session_memory[session_key]

    # 5. LLM请求去重：相同Prompt+上下文查缓存
    user_id = getattr(companion, 'user_id', 'anonymous')
    cache_key = await get_llm_cache_key(user_id, request.companion_id, system_prompt, context + [{"role": "user", "content": request.message}])
    cached_resp = await get_cached_llm_response(cache_key)
    if cached_resp:
        response = cached_resp
    else:
        # 6. 添加用户消息到上下文
        context.append({
            "role": "user",
            "content": request.message
        })
        # 7. 构建完整消息列表
        messages = [
            {"role": "system", "content": system_prompt}
        ] + context[-settings.MAX_CONTEXT_MESSAGES:]
        # 8. 调用LLM服务
        response = await llm_service.chat_completion(messages)
        # 9. 写入缓存
        await set_cached_llm_response(cache_key, response)
        # 10. 添加助手回复到上下文
        context.append({
            "role": "assistant",
            "content": response
        })
    
    # 11. 缓存到热门对话（如果是新的高质量回复）
    await hot_conversation_cache.cache_response(
        companion.personality_archetype, request.message, response
    )

    # 12. 保存消息到数据库
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


@router.post("/feedback")
async def feedback(
    companion_id: int = Body(...),
    message_id: int = Body(...),
    score: int = Body(...),  # 1=点赞，-1=点踩
    db: AsyncSession = Depends(get_db)
):
    """对对话消息进行质量反馈"""
    result = await db.execute(select(Message).where(Message.id == message_id, Message.companion_id == companion_id))
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    # 获取伙伴信息用于埋点
    companion_result = await db.execute(select(Companion).where(Companion.id == companion_id))
    companion = companion_result.scalar_one_or_none()
    
    # 假设Message表有feedback_score字段，否则可扩展新表
    if not hasattr(msg, 'feedback_score'):
        # 动态添加属性（如需持久化请在models中添加字段）
        msg.feedback_score = score
    else:
        msg.feedback_score = score
    await db.commit()
    
    # 埋点：记录对话质量反馈
    if companion:
        prompt_version = getattr(companion, 'prompt_version', 'v1')
        await analytics_service.track_conversation_quality(
            companion.user_id, companion_id, message_id, score, prompt_version
        )
    
    return {"message": "反馈已记录"}
