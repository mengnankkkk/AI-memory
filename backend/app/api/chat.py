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
from app.services.redis_utils import redis_affinity_manager, redis_event_manager
from app.services.affinity_engine import affinity_engine
from app.services.response_coordinator import response_coordinator  # 新增：响应协调器
import json
import logging

logger = logging.getLogger("chat_api")

router = APIRouter(prefix="/chat", tags=["chat"])

# 简单的内存会话存储 (生产环境应使用Redis)
session_memory: Dict[str, List[Dict[str, str]]] = {}


@router.post("/v2", response_model=ChatResponse)
async def chat_v2(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    处理聊天请求 - 双阶段"心流"交互协议完整版 (V2)

    完整的双阶段架构：
    阶段1: 情感分析 + 状态更新 + 表现生成
    阶段2: 动态提示词构建 + LLM生成回复

    特性：
    - 完整的情感表现JSON生成
    - 智能的动态提示词构建
    - 三层记忆融合（L1/L2/L3）
    - 优化的token管理
    """
    # ========== 第一步：获取伙伴信息和当前状态 ==========
    result = await db.execute(
        select(Companion).where(Companion.id == request.companion_id)
    )
    companion = result.scalar_one_or_none()
    if not companion:
        raise HTTPException(status_code=404, detail="伙伴不存在")

    companion_state = await redis_affinity_manager.get_companion_state(
        companion.user_id, request.companion_id
    )

    # 提取当前状态
    current_affinity_score = companion_state.get("affinity_score", 50) if companion_state else 50
    current_trust_score = companion_state.get("trust_score", 50) if companion_state else 50
    current_tension_score = companion_state.get("tension_score", 0) if companion_state else 0
    current_mood = companion_state.get("current_mood", "neutral") if companion_state else "neutral"
    current_level = companion_state.get("romance_level", "stranger") if companion_state else "stranger"

    logger.info(
        f"[ChatV2] 开始处理 - 用户:{companion.user_id}, "
        f"伙伴:{request.companion_id}, 等级:{current_level}"
    )

    # ========== 第二步：获取对话历史（用于L1工作记忆） ==========
    session_key = f"{request.companion_id}:{request.session_id}"
    if session_key not in session_memory:
        session_memory[session_key] = []
    conversation_history = session_memory[session_key].copy()

    # ========== 第三步：使用ResponseCoordinator执行完整的双阶段协议 ==========
    try:
        coordinated_response = await response_coordinator.coordinate_response(
            # 用户输入
            user_message=request.message,
            user_id=companion.user_id,
            # 伙伴信息
            companion_id=request.companion_id,
            companion_name=companion.name,
            # 当前状态
            current_affinity_score=current_affinity_score,
            current_trust_score=current_trust_score,
            current_tension_score=current_tension_score,
            current_level=current_level,
            current_mood=current_mood,
            # 可选参数
            conversation_history=conversation_history,
            enable_memory=True,  # 启用记忆系统
            special_instructions=None,
            debug_mode=False  # 生产环境关闭debug
        )

        response = coordinated_response.ai_response
        process_result = coordinated_response.process_result

        logger.info(
            f"[ChatV2] 双阶段协议完成 - "
            f"情感:{coordinated_response.emotion_analysis.primary_emotion}, "
            f"回复长度:{len(response)}"
        )

    except Exception as e:
        logger.error(f"[ChatV2] 响应协调失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成回复失败: {str(e)}")

    # ========== 第四步：更新所有状态到Redis ==========
    await redis_affinity_manager.update_affinity(
        companion.user_id,
        request.companion_id,
        process_result.affinity_change,
        process_result.trust_change,
        process_result.tension_change,
        "chat"
    )

    # 添加到记忆（如果值得记忆）
    if process_result.emotion_analysis.is_memorable:
        await redis_affinity_manager.add_memory(
            companion.user_id,
            request.companion_id,
            request.message,
            "conversation"
        )

    # 记录等级变化
    if process_result.level_changed:
        level_change_msg = "升级 ⬆️" if process_result.level_up else "降级 ⬇️"
        logger.info(
            f"[ChatV2] 好感度等级{level_change_msg}: {current_level} → {process_result.new_level} "
            f"({current_affinity_score} → {process_result.new_affinity_score})"
        )

    # ========== 第五步：更新会话记忆 ==========
    session_memory[session_key].append({"role": "user", "content": request.message})
    session_memory[session_key].append({"role": "assistant", "content": response})

    # 限制历史长度
    if len(session_memory[session_key]) > settings.MAX_CONTEXT_MESSAGES:
        session_memory[session_key] = session_memory[session_key][-settings.MAX_CONTEXT_MESSAGES:]

    # ========== 第六步：埋点和分析 ==========
    prompt_version = "v2_flow_protocol"  # 新版本标识
    await analytics_service.track_prompt_usage(
        companion.user_id, request.companion_id, prompt_version, companion.personality_archetype
    )

    # ========== 第七步：特殊事件触发 ==========
    updated_state = await redis_affinity_manager.get_companion_state(
        companion.user_id, request.companion_id
    )
    if updated_state and updated_state.get("total_interactions", 0) % 10 == 0:
        import random
        if random.random() < 0.3:
            event = await redis_event_manager.trigger_random_event(
                companion.user_id, request.companion_id
            )
            if event:
                logger.info(f"[ChatV2] 触发随机事件: {event['title']}")

    # ========== 第八步：保存消息到数据库 ==========
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

    logger.info(f"[ChatV2] 消息处理完成")
    return ChatResponse(
        message=response,
        companion_name=companion.name
    )


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    处理聊天请求 - AI情感计算引擎集成版 (V1 - 兼容版)

    采用两阶段LLM调用架构：
    Pass 1: 情感分析与评估 (由AffinityEngine完成)
    Pass 2: 生成最终回复 (本函数完成)

    注意：建议使用 /chat/v2 获得完整的双阶段"心流"体验
    """
    # ========== 第一步：获取伙伴信息和当前状态 ==========
    result = await db.execute(
        select(Companion).where(Companion.id == request.companion_id)
    )
    companion = result.scalar_one_or_none()
    if not companion:
        raise HTTPException(status_code=404, detail="伙伴不存在")

    companion_state = await redis_affinity_manager.get_companion_state(
        companion.user_id, request.companion_id
    )

    # 提取当前状态
    current_affinity_score = companion_state.get("affinity_score", 50) if companion_state else 50
    current_trust_score = companion_state.get("trust_score", 50) if companion_state else 50
    current_tension_score = companion_state.get("tension_score", 0) if companion_state else 0
    current_mood = companion_state.get("current_mood", "平静") if companion_state else "平静"
    current_level = companion_state.get("romance_level", "stranger") if companion_state else "stranger"

    # TODO: 集成记忆系统（如果存在）
    recent_memories = None  # 从L2情景记忆获取
    user_facts = None  # 从L3语义记忆获取

    # ========== 第二步：调用AffinityEngine处理消息 (Pass 1) ==========
    logger.info(f"[Chat] 开始处理消息 - 用户:{companion.user_id}, 伙伴:{request.companion_id}")

    process_result = await affinity_engine.process_user_message(
        user_message=request.message,
        current_affinity_score=current_affinity_score,
        current_trust_score=current_trust_score,
        current_tension_score=current_tension_score,
        current_level=current_level,
        current_mood=current_mood,
        companion_name=companion.name,
        user_id=companion.user_id,
        companion_id=request.companion_id,
        recent_memories=recent_memories,
        user_facts=user_facts
    )

    # ========== 第三步：更新所有状态到Redis ==========
    await redis_affinity_manager.update_affinity(
        companion.user_id,
        request.companion_id,
        process_result.affinity_change,
        process_result.trust_change,
        process_result.tension_change,
        "chat"
    )

    # 添加到记忆（如果值得记忆）
    if process_result.emotion_analysis.is_memorable:
        await redis_affinity_manager.add_memory(
            companion.user_id,
            request.companion_id,
            request.message,
            "conversation"
        )

    # 记录等级变化
    if process_result.level_changed:
        level_change_msg = "升级 ⬆️" if process_result.level_up else "降级 ⬇️"
        logger.info(
            f"[Chat] 好感度等级{level_change_msg}: {current_level} → {process_result.new_level} "
            f"({current_affinity_score} → {process_result.new_affinity_score})"
        )

    # 埋点
    prompt_version = getattr(companion, 'prompt_version', 'v1')
    await analytics_service.track_prompt_usage(
        companion.user_id, request.companion_id, prompt_version, companion.personality_archetype
    )

    # ========== 第四步：检查缓存 ==========
    hot_response = await hot_conversation_cache.get_cached_response(
        companion.personality_archetype, request.message
    )
    if hot_response:
        logger.info(f"[Chat] 使用热门对话缓存")
        response = hot_response
    else:
        # ========== 第五步：调用LLM生成最终回复 (Pass 2) ==========
        session_key = f"{request.companion_id}:{request.session_id}"
        if session_key not in session_memory:
            session_memory[session_key] = []
        context = session_memory[session_key]

        # LLM请求去重
        cache_key = await get_llm_cache_key(
            companion.user_id, request.companion_id,
            process_result.enhanced_system_prompt,
            context + [{"role": "user", "content": request.message}]
        )
        cached_resp = await get_cached_llm_response(cache_key)

        if cached_resp:
            response = cached_resp
        else:
            context.append({"role": "user", "content": request.message})
            messages = [
                {"role": "system", "content": process_result.enhanced_system_prompt}
            ] + context[-settings.MAX_CONTEXT_MESSAGES:]

            logger.info(f"[Chat] 调用LLM生成回复 (Pass 2)")
            response = await llm_service.chat_completion(messages)

            await set_cached_llm_response(cache_key, response)
            context.append({"role": "assistant", "content": response})

        # 缓存高质量回复
        await hot_conversation_cache.cache_response(
            companion.personality_archetype, request.message, response
        )

    # ========== 第六步：特殊事件触发 ==========
    updated_state = await redis_affinity_manager.get_companion_state(
        companion.user_id, request.companion_id
    )
    if updated_state and updated_state.get("total_interactions", 0) % 10 == 0:
        import random
        if random.random() < 0.3:
            event = await redis_event_manager.trigger_random_event(
                companion.user_id, request.companion_id
            )
            if event:
                logger.info(f"[Chat] 触发随机事件: {event['title']}")

    # ========== 第七步：保存消息到数据库 ==========
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

    logger.info(f"[Chat] 消息处理完成")
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
