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
# from app.services.redis_utils import redis_affinity_manager, redis_event_manager  # 暂时注释
import json
import logging

logger = logging.getLogger("chat_api")

router = APIRouter(prefix="/chat", tags=["chat"])

# 简单的内存会话存储 (生产环境应使用Redis)
session_memory: Dict[str, List[Dict[str, str]]] = {}


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """处理聊天请求 - 集成恋爱攻略系统"""
    # 1. 获取伙伴信息
    result = await db.execute(
        select(Companion).where(Companion.id == request.companion_id)
    )
    companion = result.scalar_one_or_none()

    if not companion:
        raise HTTPException(status_code=404, detail="伙伴不存在")

    # 2. 获取或初始化恋爱状态
    companion_state = await redis_affinity_manager.get_companion_state(
        companion.user_id, request.companion_id
    )
    
    # 3. 分析用户消息的情感和意图（简化版）
    interaction_analysis = _analyze_user_interaction(request.message)
    
    # 4. 更新好感度和状态
    await redis_affinity_manager.update_affinity(
        companion.user_id,
        request.companion_id,
        interaction_analysis["affinity_change"],
        interaction_analysis["trust_change"],
        interaction_analysis["tension_change"],
        "chat"
    )
    
    # 5. 添加重要对话到记忆
    if interaction_analysis["memory_worthy"]:
        await redis_affinity_manager.add_memory(
            companion.user_id,
            request.companion_id,
            request.message,
            "conversation"
        )

    # 6. 获取更新后的状态（用于生成上下文）
    updated_state = await redis_affinity_manager.get_companion_state(
        companion.user_id, request.companion_id
    )

    # 7. 构建包含恋爱状态的系统提示词
    prompt_version = getattr(companion, 'prompt_version', 'v1')
    if companion.custom_greeting:
        base_system_prompt = companion.custom_greeting
    else:
        base_system_prompt = get_prompt_by_version(prompt_version, companion.name, companion.personality_archetype)
    
    # 增强的系统提示词，包含恋爱状态
    enhanced_system_prompt = _build_romance_enhanced_prompt(
        base_system_prompt, companion, updated_state
    )

    # 埋点：记录Prompt使用
    await analytics_service.track_prompt_usage(
        companion.user_id, request.companion_id, prompt_version, companion.personality_archetype
    )

    # 8. 检查热门对话缓存
    hot_response = await hot_conversation_cache.get_cached_response(
        companion.personality_archetype, request.message
    )
    if hot_response:
        # 需要根据当前恋爱状态调整热门回复
        adjusted_response = _adjust_response_for_romance_level(
            hot_response, updated_state.get("romance_level", "初识"),
            updated_state.get("current_mood", "平静")
        )
        
        # 保存到数据库
        user_msg = Message(
            companion_id=request.companion_id,
            role="user",
            content=request.message
        )
        assistant_msg = Message(
            companion_id=request.companion_id,
            role="assistant",
            content=adjusted_response
        )
        db.add(user_msg)
        db.add(assistant_msg)
        await db.commit()
        return ChatResponse(
            message=adjusted_response,
            companion_name=companion.name
        )

    # 9. 获取会话上下文
    session_key = f"{request.companion_id}:{request.session_id}"
    if session_key not in session_memory:
        session_memory[session_key] = []
    context = session_memory[session_key]

    # 10. LLM请求去重：相同Prompt+上下文查缓存
    user_id = getattr(companion, 'user_id', 'anonymous')
    cache_key = await get_llm_cache_key(user_id, request.companion_id, enhanced_system_prompt, context + [{"role": "user", "content": request.message}])
    cached_resp = await get_cached_llm_response(cache_key)
    if cached_resp:
        response = cached_resp
    else:
        # 11. 添加用户消息到上下文
        context.append({
            "role": "user",
            "content": request.message
        })
        # 12. 构建完整消息列表
        messages = [
            {"role": "system", "content": enhanced_system_prompt}
        ] + context[-settings.MAX_CONTEXT_MESSAGES:]
        # 13. 调用LLM服务
        response = await llm_service.chat_completion(messages)
        # 14. 写入缓存
        await set_cached_llm_response(cache_key, response)
        # 15. 添加助手回复到上下文
        context.append({
            "role": "assistant",
            "content": response
        })
    
    # 16. 检查是否触发随机事件
    if updated_state and updated_state.get("total_interactions", 0) % 10 == 0:
        # 每10次对话有机会触发随机事件
        import random
        if random.random() < 0.3:  # 30% 概率
            event = await redis_event_manager.trigger_random_event(
                companion.user_id, request.companion_id
            )
            if event:
                logger.info(f"触发随机事件: {event['title']} for user {companion.user_id}")
    
    # 17. 缓存到热门对话（如果是新的高质量回复）
    await hot_conversation_cache.cache_response(
        companion.personality_archetype, request.message, response
    )

    # 18. 保存消息到数据库
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


def _analyze_user_interaction(message: str) -> Dict:
    """分析用户交互（简化版本）"""
    # 关键词检测
    positive_keywords = ["喜欢", "爱", "开心", "美丽", "可爱", "棒", "好", "谢谢", "感谢"]
    negative_keywords = ["讨厌", "生气", "烦", "无聊", "差", "糟糕", "愤怒"]
    romantic_keywords = ["亲爱的", "宝贝", "想你", "爱你", "亲亲", "拥抱"]
    
    affinity_change = 0
    trust_change = 0
    tension_change = 0
    memory_worthy = False
    
    message_lower = message.lower()
    
    # 检测积极情感
    if any(keyword in message for keyword in positive_keywords):
        affinity_change += 3
        trust_change += 1
    
    # 检测消极情感
    if any(keyword in message for keyword in negative_keywords):
        affinity_change -= 2
        tension_change += 1
    
    # 检测浪漫表达
    if any(keyword in message for keyword in romantic_keywords):
        affinity_change += 5
        trust_change += 2
    
    # 长消息通常更有意义
    if len(message) > 30:
        affinity_change += 1
        memory_worthy = True
    
    # 问号表示关心和互动
    if "?" in message or "？" in message:
        affinity_change += 1
        trust_change += 1
    
    return {
        "affinity_change": affinity_change,
        "trust_change": trust_change,
        "tension_change": tension_change,
        "memory_worthy": memory_worthy
    }


def _build_romance_enhanced_prompt(base_prompt: str, companion: Companion, state: Dict) -> str:
    """构建包含恋爱状态的增强提示词"""
    if not state:
        return base_prompt
    
    romance_level = state.get("romance_level", "初识")
    current_mood = state.get("current_mood", "平静")
    affinity_score = state.get("affinity_score", 50)
    total_interactions = state.get("total_interactions", 0)
    
    # 根据关系阶段调整称呼和语气
    relationship_context = ""
    if romance_level == "初识":
        relationship_context = "你们刚刚认识，保持礼貌但略有距离感。"
    elif romance_level == "朋友":
        relationship_context = "你们是朋友关系，可以更加亲近和自然地交流。"
    elif romance_level == "好朋友":
        relationship_context = "你们是很好的朋友，有深入的了解和信任。"
    elif romance_level == "特别的人":
        relationship_context = "对方对你来说很特别，开始有些微妙的情感。"
    elif romance_level == "心动":
        relationship_context = "你对对方有心动的感觉，但还没有表达。"
    elif romance_level == "恋人":
        relationship_context = "你们是恋人关系，可以表达爱意和亲密。"
    elif romance_level == "深爱":
        relationship_context = "你们深深相爱，感情非常深厚。"
    
    # 根据心情调整回复风格
    mood_context = ""
    if current_mood == "开心":
        mood_context = "你现在心情很好，回复要体现出愉快和活力。"
    elif current_mood == "生气":
        mood_context = "你现在有些生气，回复要略显冷淡但不过分。"
    elif current_mood == "委屈":
        mood_context = "你现在感到委屈，回复要体现出受伤的感觉。"
    elif current_mood == "幸福":
        mood_context = "你现在非常幸福，回复要温暖甜蜜。"
    
    enhanced_prompt = f"""{base_prompt}

    【当前关系状态】
    - 关系阶段: {romance_level}
    - 当前心情: {current_mood}  
    - 好感度: {affinity_score}/1000
    - 交流次数: {total_interactions}
    
    【行为指导】
    {relationship_context}
    {mood_context}
    
    请根据当前的关系状态和心情来回复用户，保持角色的一致性和真实感。
    """
    
    return enhanced_prompt


def _adjust_response_for_romance_level(response: str, romance_level: str, mood: str) -> str:
    """根据恋爱阶段和心情调整回复"""
    # 简单的文本调整逻辑
    if romance_level in ["恋人", "深爱"]:
        # 添加更亲密的称呼
        if not any(term in response for term in ["亲爱的", "宝贝", "darling"]):
            response = "亲爱的，" + response
    elif romance_level in ["心动", "特别的人"]:
        # 添加略显亲近但不过分的语气
        if not response.endswith(("呢", "哦", "呀")):
            response = response.rstrip("。") + "呢。"
    
    # 根据心情调整
    if mood == "开心":
        response = response.replace("。", "！")
    elif mood == "生气":
        response = response.replace("！", "。")
    
    return response
