"""
恋爱攻略系统 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.companion import Companion
from app.models.gift import UserGiftInventory
from app.api.schemas_romance import (
    CompanionStateResponse, GiftRequest, GiftResponse,
    RandomEventResponse, InteractionAnalysisRequest, InteractionAnalysisResponse,
    DailyTaskResponse, StoreItemResponse, UserCurrencyResponse
)
from app.services.redis_utils import (
    redis_affinity_manager, redis_event_manager, redis_stats_manager
)
from app.services.task_manager import task_manager
from app.core.gift_config import get_all_gifts, get_gift_by_id
from typing import List, Optional
import logging
import json
import time
from datetime import datetime, timedelta

logger = logging.getLogger("romance_api")
router = APIRouter(prefix="/romance", tags=["romance"])


@router.get("/companion/{companion_id}/state", response_model=CompanionStateResponse)
async def get_companion_state(
    companion_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取伙伴的恋爱状态"""
    try:
        # 验证伙伴是否存在（区分系统伙伴和用户自建伙伴）
        stmt = select(Companion).where(Companion.id == companion_id)
        result = await db.execute(stmt)
        companion = result.scalar_one_or_none()

        if not companion:
            raise HTTPException(status_code=404, detail="伙伴不存在")

        # 系统伙伴（user_id=1）对所有用户可见，用户自建伙伴只对创建者可见
        if companion.user_id != 1 and companion.user_id != int(user_id):
            raise HTTPException(status_code=403, detail="无权访问此伙伴")
        
        # 获取状态
        state = await redis_affinity_manager.get_companion_state(user_id, companion_id)
        if not state:
            raise HTTPException(status_code=500, detail="无法获取伙伴状态")
        
        return CompanionStateResponse(**state)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[get_companion_state] {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/companion/{companion_id}/gift", response_model=GiftResponse)
async def give_gift(
    companion_id: int,
    gift_request: GiftRequest,
    db: AsyncSession = Depends(get_db)
):
    """赠送礼物给伙伴"""
    try:
        # 验证伙伴是否存在（区分系统伙伴和用户自建伙伴）
        stmt = select(Companion).where(Companion.id == companion_id)
        result = await db.execute(stmt)
        companion = result.scalar_one_or_none()

        if not companion:
            raise HTTPException(status_code=404, detail="伙伴不存在")

        # 系统伙伴（user_id=1）对所有用户可见，用户自建伙伴只对创建者可见
        if companion.user_id != 1 and companion.user_id != int(gift_request.user_id):
            raise HTTPException(status_code=403, detail="无权访问此伙伴")

        # 获取礼物配置
        gift_config = get_gift_by_id(gift_request.gift_type)
        if not gift_config:
            raise HTTPException(status_code=400, detail="未知的礼物类型")

        # 检查用户库存
        stmt_inventory = select(UserGiftInventory).where(
            UserGiftInventory.user_id == gift_request.user_id,
            UserGiftInventory.gift_id == gift_request.gift_type
        )
        result_inventory = await db.execute(stmt_inventory)
        inventory = result_inventory.scalar_one_or_none()

        if not inventory or inventory.quantity <= 0:
            raise HTTPException(status_code=400, detail=f"库存不足！{gift_config['name']}数量为0")

        # 扣除库存
        inventory.quantity -= 1
        await db.commit()

        # 获取赠送前的状态
        old_state = await redis_affinity_manager.get_companion_state(
            gift_request.user_id, companion_id
        )
        old_affinity = old_state.get("affinity_score", 50) if old_state else 50

        # 使用配置中的好感度增益
        await redis_affinity_manager.update_affinity(
            gift_request.user_id,
            companion_id,
            gift_config["affinity_bonus"],
            gift_config.get("trust_bonus", 0),
            gift_config.get("tension_bonus", 0),
            "gift"
        )

        # 获取赠送后的状态
        new_state = await redis_affinity_manager.get_companion_state(
            gift_request.user_id, companion_id
        )
        new_affinity = new_state.get("affinity_score", 50) if new_state else 50
        affinity_change = new_affinity - old_affinity

        # 生成伙伴反应（使用英文键名）
        companion_reaction = _generate_gift_reaction(
            gift_request.gift_type, companion.personality_archetype,
            new_state.get("romance_level", "stranger")
        )

        # 记录统计
        await redis_stats_manager.increment_counter("gifts_given")
        await redis_stats_manager.increment_counter(f"gift_type_{gift_request.gift_type}")

        # 自动完成礼物任务
        auto_complete_result = await task_manager.check_and_complete_task_automatically(
            gift_request.user_id, companion_id, "gift"
        )
        if auto_complete_result:
            logger.info(f"[GiftSystem] 自动完成礼物任务，奖励: {auto_complete_result['reward']}")
            # 更新好感度
            await redis_affinity_manager.update_affinity(
                gift_request.user_id, companion_id,
                auto_complete_result['reward'], 0, 0, "task"
            )

        logger.info(f"[GiftSystem] {gift_request.user_id} 赠送 {gift_config['name']} 给 {companion.name}，库存剩余: {inventory.quantity}")

        return GiftResponse(
            success=True,
            message=f"成功赠送{gift_config['name']}（剩余{inventory.quantity}个）",
            affinity_change=affinity_change,
            new_affinity_score=new_affinity,
            companion_reaction=companion_reaction
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[give_gift] {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/companion/{companion_id}/random-event", response_model=RandomEventResponse)
async def trigger_random_event(
    companion_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """触发随机事件"""
    try:
        # 验证伙伴是否存在（区分系统伙伴和用户自建伙伴）
        stmt = select(Companion).where(Companion.id == companion_id)
        result = await db.execute(stmt)
        companion = result.scalar_one_or_none()

        if not companion:
            raise HTTPException(status_code=404, detail="伙伴不存在")

        # 系统伙伴（user_id=1）对所有用户可见，用户自建伙伴只对创建者可见
        if companion.user_id != 1 and companion.user_id != int(user_id):
            raise HTTPException(status_code=403, detail="无权访问此伙伴")
        
        # 触发随机事件
        event = await redis_event_manager.trigger_random_event(user_id, companion_id)
        
        if event:
            # 记录统计
            await redis_stats_manager.increment_counter("random_events_triggered")
            await redis_stats_manager.increment_counter(f"event_type_{event['type']}")
            
            return RandomEventResponse(
                event=event,
                triggered=True
            )
        else:
            return RandomEventResponse(
                event=None,
                triggered=False
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[trigger_random_event] {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/companion/{companion_id}/pending-events")
async def get_pending_events(
    companion_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取待处理事件"""
    try:
        # 验证伙伴是否存在（区分系统伙伴和用户自建伙伴）
        stmt = select(Companion).where(Companion.id == companion_id)
        result = await db.execute(stmt)
        companion = result.scalar_one_or_none()

        if not companion:
            raise HTTPException(status_code=404, detail="伙伴不存在")

        # 系统伙伴（user_id=1）对所有用户可见，用户自建伙伴只对创建者可见
        if companion.user_id != 1 and companion.user_id != int(user_id):
            raise HTTPException(status_code=403, detail="无权访问此伙伴")
        
        # 获取待处理事件
        events = await redis_event_manager.get_pending_events(user_id, companion_id)
        
        return {"events": events}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[get_pending_events] {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/companion/{companion_id}/analyze-interaction", response_model=InteractionAnalysisResponse)
async def analyze_interaction(
    companion_id: int,
    analysis_request: InteractionAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """分析用户交互并更新好感度"""
    try:
        # 验证伙伴是否存在（区分系统伙伴和用户自建伙伴）
        stmt = select(Companion).where(Companion.id == companion_id)
        result = await db.execute(stmt)
        companion = result.scalar_one_or_none()

        if not companion:
            raise HTTPException(status_code=404, detail="伙伴不存在")

        # 系统伙伴（user_id=1）对所有用户可见，用户自建伙伴只对创建者可见
        if companion.user_id != 1 and companion.user_id != int(analysis_request.user_id):
            raise HTTPException(status_code=403, detail="无权访问此伙伴")
        
        # 分析用户消息
        analysis = _analyze_user_message(
            analysis_request.message,
            analysis_request.interaction_type,
            companion.personality_archetype
        )
        
        # 更新好感度
        await redis_affinity_manager.update_affinity(
            analysis_request.user_id,
            companion_id,
            analysis["affinity_change"],
            analysis["trust_change"],
            analysis["tension_change"],
            analysis_request.interaction_type
        )
        
        # 如果值得记忆，添加到记忆中
        if analysis["memory_worthy"]:
            await redis_affinity_manager.add_memory(
                analysis_request.user_id,
                companion_id,
                analysis_request.message,
                analysis_request.interaction_type
            )
        
        # 记录统计
        await redis_stats_manager.increment_counter("interactions_analyzed")
        await redis_stats_manager.increment_counter(f"sentiment_{analysis['sentiment']}")

        # 自动检测并完成任务
        auto_complete_tasks = []

        # 检测聊天任务（每次对话都计数）
        chat_result = await task_manager.check_and_complete_task_automatically(
            analysis_request.user_id, companion_id, "chat"
        )
        if chat_result:
            auto_complete_tasks.append(("chat", chat_result))

        # 检测赞美任务
        if analysis["sentiment"] == "positive":
            compliment_result = await task_manager.check_and_complete_task_automatically(
                analysis_request.user_id, companion_id, "compliment", analysis_request.message
            )
            if compliment_result:
                auto_complete_tasks.append(("compliment", compliment_result))

        # 检测浪漫任务
        romantic_result = await task_manager.check_and_complete_task_automatically(
            analysis_request.user_id, companion_id, "romantic", analysis_request.message
        )
        if romantic_result:
            auto_complete_tasks.append(("romantic", romantic_result))

        # 为所有自动完成的任务更新好感度
        for task_type, result in auto_complete_tasks:
            logger.info(f"[InteractionAnalysis] 自动完成{task_type}任务，奖励: {result['reward']}")
            await redis_affinity_manager.update_affinity(
                analysis_request.user_id, companion_id,
                result['reward'], 0, 0, "task"
            )

        return InteractionAnalysisResponse(**analysis)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[analyze_interaction] {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/companion/{companion_id}/daily-tasks", response_model=List[DailyTaskResponse])
async def get_daily_tasks(
    companion_id: int,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取每日任务"""
    try:
        # 验证伙伴是否存在（区分系统伙伴和用户自建伙伴）
        stmt = select(Companion).where(Companion.id == companion_id)
        result = await db.execute(stmt)
        companion = result.scalar_one_or_none()

        if not companion:
            raise HTTPException(status_code=404, detail="伙伴不存在")

        # 系统伙伴（user_id=1）对所有用户可见，用户自建伙伴只对创建者可见
        if companion.user_id != 1 and companion.user_id != int(user_id):
            raise HTTPException(status_code=403, detail="无权访问此伙伴")
        
        # 获取伙伴状态以确定任务难度（使用英文键名）
        state = await redis_affinity_manager.get_companion_state(user_id, companion_id)
        romance_level = state.get("romance_level", "stranger") if state else "stranger"

        # 使用TaskManager生成每日任务
        tasks = await task_manager.generate_daily_tasks(
            user_id, companion_id, romance_level, companion.personality_archetype
        )

        return tasks

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[get_daily_tasks] {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/companion/{companion_id}/tasks/{task_id}/complete")
async def complete_task(
    companion_id: int,
    task_id: str,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """完成每日任务"""
    try:
        # 验证伙伴是否存在
        stmt = select(Companion).where(Companion.id == companion_id)
        result = await db.execute(stmt)
        companion = result.scalar_one_or_none()

        if not companion:
            raise HTTPException(status_code=404, detail="伙伴不存在")

        # 系统伙伴（user_id=1）对所有用户可见，用户自建伙伴只对创建者可见
        if companion.user_id != 1 and companion.user_id != int(user_id):
            raise HTTPException(status_code=403, detail="无权访问此伙伴")

        # 完成任务
        task_result = await task_manager.complete_task(user_id, companion_id, task_id)

        if not task_result["success"]:
            return task_result

        # 获取奖励好感度
        reward = task_result["reward"]

        # 更新好感度
        await redis_affinity_manager.update_affinity(
            user_id,
            companion_id,
            reward,  # affinity_change
            0,       # trust_change
            0,       # tension_change
            "task"   # interaction_type
        )

        # 记录统计
        await redis_stats_manager.increment_counter("tasks_completed")
        await redis_stats_manager.increment_counter(f"task_type_{task_id.split('_')[1]}")

        logger.info(f"[TaskSystem] {user_id} 完成任务 {task_id}，获得 {reward} 好感度")

        return {
            "success": True,
            "message": task_result["message"],
            "reward": reward,
            "task_id": task_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[complete_task] {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/store/items", response_model=List[StoreItemResponse])
async def get_store_items(
    user_id: str = Query(..., description="用户ID"),
    item_type: Optional[str] = Query(None, description="物品类型"),
    rarity: Optional[str] = Query(None, description="稀有度"),
    db: AsyncSession = Depends(get_db)
):
    """获取商店物品（含用户库存）"""
    try:
        # 获取所有礼物配置
        gift_configs = get_all_gifts()

        # 获取用户库存
        stmt = select(UserGiftInventory).where(UserGiftInventory.user_id == user_id)
        result = await db.execute(stmt)
        inventories = result.scalars().all()

        # 创建库存字典
        inventory_dict = {inv.gift_id: inv.quantity for inv in inventories}

        # 构建礼物列表
        items = []
        for gift in gift_configs:
            # 过滤条件
            if item_type and gift["gift_type"] != item_type:
                continue
            if rarity and gift["rarity"] != rarity:
                continue

            item = StoreItemResponse(
                item_id=gift["gift_id"],
                item_type=gift["gift_type"],
                name=gift["name"],
                description=gift["description"],
                price=gift["price"],
                currency=gift["currency"],
                preview_url=gift.get("emoji", "🎁"),  # 使用emoji作为预览
                rarity=gift["rarity"],
                quantity=inventory_dict.get(gift["gift_id"], 0)  # 添加库存数量
            )
            items.append(item)

        return items

    except Exception as e:
        logger.error(f"[get_store_items] {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/user/{user_id}/currency", response_model=UserCurrencyResponse)
async def get_user_currency(user_id: str):
    """获取用户货币信息"""
    try:
        # 这里应该从Redis或数据库中读取用户货币信息
        # 目前返回示例数据
        currency_data = await _get_user_currency(user_id)
        return currency_data
    
    except Exception as e:
        logger.error(f"[get_user_currency] {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


# 辅助函数
def _generate_gift_reaction(gift_type: str, personality_type: str, romance_level: str) -> str:
    """生成礼物反应（使用英文键名匹配）"""
    # 礼物反应字典 - 使用英文键名与affinity_levels.py保持一致
    reactions = {
        "flower": {
            "stranger": "谢谢你的花，很漂亮呢。",
            "acquaintance": "哇，这束花真的很美！谢谢你想到我。",
            "friend": "这束花让我想起我们一起度过的美好时光。",
            "romantic": "你总是知道怎么让我开心...这些花就像你对我的心意一样美丽。",
            "lover": "每一朵花都代表着你对我的爱，我会好好珍惜的。"
        },
        "chocolate": {
            "stranger": "巧克力...谢谢，我会好好品尝的。",
            "acquaintance": "我最喜欢巧克力了！你怎么知道的？",
            "friend": "又是我喜欢的口味！你真了解我。",
            "romantic": "每次吃到你给的巧克力，都感觉甜到心里了。",
            "lover": "巧克力的甜蜜就像我们之间的感情一样浓郁~"
        }
    }

    default_reaction = "谢谢你的礼物，我很喜欢！"
    return reactions.get(gift_type, {}).get(romance_level, default_reaction)


def _analyze_user_message(message: str, interaction_type: str, personality_type: str) -> dict:
    """分析用户消息（简化版，实际应该使用LLM）"""
    # 简化的规则引擎分析
    sentiment = "neutral"
    affinity_change = 0
    trust_change = 0
    tension_change = 0
    memory_worthy = False
    
    # 关键词检测
    positive_keywords = ["喜欢", "爱", "开心", "美丽", "可爱", "棒", "好"]
    negative_keywords = ["讨厌", "生气", "烦", "无聊", "差"]
    
    message_lower = message.lower()
    
    if any(keyword in message for keyword in positive_keywords):
        sentiment = "positive"
        affinity_change = 5
        trust_change = 1
    elif any(keyword in message for keyword in negative_keywords):
        sentiment = "negative"
        affinity_change = -3
        tension_change = 2
    
    # 检测是否值得记忆
    if len(message) > 20 or sentiment != "neutral":
        memory_worthy = True
    
    return {
        "sentiment": sentiment,
        "user_intent": interaction_type,
        "topics": ["general"],
        "affinity_change": affinity_change,
        "trust_change": trust_change,
        "tension_change": tension_change,
        "suggested_ai_mood": "happy" if sentiment == "positive" else "sad" if sentiment == "negative" else "neutral",
        "memory_worthy": memory_worthy
    }


def _generate_daily_tasks(romance_level: str, personality_type: str) -> List[DailyTaskResponse]:
    """生成每日任务"""
    base_tasks = [
        {
            "task_id": f"daily_chat_{datetime.now().strftime('%Y%m%d')}",
            "task_type": "chat",
            "description": "与伙伴聊天10分钟",
            "reward_affinity": 5,
            "completed": False,
            "deadline": datetime.now() + timedelta(hours=24)
        },
        {
            "task_id": f"daily_compliment_{datetime.now().strftime('%Y%m%d')}",
            "task_type": "compliment",
            "description": "给伙伴一个赞美",
            "reward_affinity": 8,
            "completed": False,
            "deadline": datetime.now() + timedelta(hours=24)
        }
    ]
    
    # 根据关系阶段添加特殊任务（使用英文键名）
    if romance_level in ["romantic", "lover"]:
        base_tasks.append({
            "task_id": f"daily_romantic_{datetime.now().strftime('%Y%m%d')}",
            "task_type": "romantic",
            "description": "说一句甜蜜的话",
            "reward_affinity": 15,
            "completed": False,
            "deadline": datetime.now() + timedelta(hours=24)
        })
    
    return [DailyTaskResponse(**task) for task in base_tasks]


def _get_store_items(item_type: Optional[str], rarity: Optional[str]) -> List[StoreItemResponse]:
    """获取商店物品（示例数据）"""
    items = [
        {
            "item_id": "flower_rose",
            "item_type": "gift",
            "name": "红玫瑰",
            "description": "经典的爱情象征",
            "price": 100,
            "currency": "coins",
            "preview_url": "/images/gifts/rose.png",
            "rarity": "common"
        },
        {
            "item_id": "outfit_dress_blue",
            "item_type": "outfit",
            "name": "蓝色连衣裙",
            "description": "优雅的蓝色连衣裙",
            "price": 500,
            "currency": "coins",
            "preview_url": "/images/outfits/blue_dress.png",
            "rarity": "rare"
        }
    ]
    
    # 过滤条件
    if item_type:
        items = [item for item in items if item["item_type"] == item_type]
    if rarity:
        items = [item for item in items if item["rarity"] == rarity]
    
    return [StoreItemResponse(**item) for item in items]


async def _get_user_currency(user_id: str) -> UserCurrencyResponse:
    """获取用户货币信息"""
    # 这里应该从Redis或数据库读取实际数据
    return UserCurrencyResponse(
        coins=1000,
        gems=50,
        daily_coins_earned=100,
        daily_limit_reached=False
    )
