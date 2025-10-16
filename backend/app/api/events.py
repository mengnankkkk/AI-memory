"""
事件系统API端点
提供事件查询、触发和完成功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import List, Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.event import Event, UserEventHistory
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/events", tags=["events"])


class EventResponse(BaseModel):
    """事件响应模型"""
    event_id: int
    event_code: str
    event_name: str
    event_type: str
    category: str
    script_content: dict
    image_url: Optional[str]
    history_id: int
    triggered_at: str
    is_completed: bool
    companion_name: Optional[str] = None

    class Config:
        from_attributes = True


class EventCompleteRequest(BaseModel):
    """完成事件请求模型"""
    choice: Optional[str] = None
    choice_content: Optional[str] = None


class EventHistoryResponse(BaseModel):
    """事件历史响应模型"""
    id: int
    event_code: str
    event_name: str
    triggered_at: str
    completed_at: Optional[str]
    is_completed: bool
    choice_made: Optional[str]

    class Config:
        from_attributes = True


@router.get("/pending", response_model=List[EventResponse])
async def get_pending_events(
    companion_id: int = Query(..., description="伙伴ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取待处理的事件

    返回用户与指定伙伴之间所有未完成的事件
    """
    try:
        stmt = select(UserEventHistory, Event).join(
            Event, UserEventHistory.event_id == Event.event_id
        ).where(
            and_(
                UserEventHistory.user_id == str(current_user.id),
                UserEventHistory.companion_id == str(companion_id),
                UserEventHistory.is_completed == False
            )
        ).order_by(UserEventHistory.triggered_at.desc())

        result = await db.execute(stmt)
        events = result.all()

        response = []
        for history, event in events:
            # 获取事件图片URL
            image_url = _get_event_image_url(companion_id, event)

            response.append(EventResponse(
                event_id=event.event_id,
                event_code=event.event_code,
                event_name=event.event_name,
                event_type=event.event_type,
                category=event.category,
                script_content=event.script_content,
                image_url=image_url,
                history_id=history.id,
                triggered_at=history.triggered_at.isoformat(),
                is_completed=history.is_completed
            ))

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取事件失败: {str(e)}")


@router.get("/history", response_model=List[EventHistoryResponse])
async def get_event_history(
    companion_id: int = Query(..., description="伙伴ID"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取事件历史记录

    返回用户与指定伙伴之间的历史事件记录
    """
    try:
        stmt = select(UserEventHistory, Event).join(
            Event, UserEventHistory.event_id == Event.event_id
        ).where(
            and_(
                UserEventHistory.user_id == str(current_user.id),
                UserEventHistory.companion_id == str(companion_id),
                UserEventHistory.is_completed == True
            )
        ).order_by(UserEventHistory.completed_at.desc()).limit(limit)

        result = await db.execute(stmt)
        events = result.all()

        response = []
        for history, event in events:
            response.append(EventHistoryResponse(
                id=history.id,
                event_code=event.event_code,
                event_name=event.event_name,
                triggered_at=history.triggered_at.isoformat(),
                completed_at=history.completed_at.isoformat() if history.completed_at else None,
                is_completed=history.is_completed,
                choice_made=history.choice_made
            ))

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@router.post("/{history_id}/complete")
async def complete_event(
    history_id: int,
    request: EventCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    完成事件

    标记事件为已完成，并记录用户的选择（如果有）
    """
    try:
        stmt = select(UserEventHistory).where(
            and_(
                UserEventHistory.id == history_id,
                UserEventHistory.user_id == str(current_user.id)
            )
        )
        result = await db.execute(stmt)
        history = result.scalar_one_or_none()

        if not history:
            raise HTTPException(status_code=404, detail="事件不存在")

        # 更新事件状态
        history.is_completed = True
        history.completed_at = datetime.now(timezone.utc)

        if request.choice:
            history.choice_made = request.choice

        if request.choice_content:
            history.choice_content = request.choice_content

        await db.commit()

        return {
            "success": True,
            "message": "事件已完成",
            "history_id": history_id
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"完成事件失败: {str(e)}")


@router.post("/{history_id}/trigger-conversation")
async def trigger_event_conversation(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    触发事件相关对话

    将事件内容注入到对话上下文，并标记事件为已完成
    """
    try:
        stmt = select(UserEventHistory, Event).join(
            Event, UserEventHistory.event_id == Event.event_id
        ).where(
            and_(
                UserEventHistory.id == history_id,
                UserEventHistory.user_id == str(current_user.id)
            )
        )
        result = await db.execute(stmt)
        event_data = result.one_or_none()

        if not event_data:
            raise HTTPException(status_code=404, detail="事件不存在")

        history, event = event_data

        # 构建事件上下文消息
        event_context = {
            "event_name": event.event_name,
            "event_description": event.script_content.get("description", ""),
            "dialogue": event.script_content.get("dialogue", [])
        }

        # 标记事件为已完成
        history.is_completed = True
        history.completed_at = datetime.now(timezone.utc)
        history.choice_made = "conversation_triggered"

        await db.commit()

        return {
            "success": True,
            "message": "事件对话已触发",
            "event_context": event_context
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"触发对话失败: {str(e)}")


def _get_event_image_url(companion_id: int, event: Event) -> Optional[str]:
    """
    获取事件图片URL

    根据伙伴ID和事件配置，返回对应的图片URL
    """
    # 角色ID映射
    personality_map = {
        1: "linzixi",
        2: "xuejian",
        3: "nagi",
        4: "shiyu",
        5: "zoe",
        6: "kevin"
    }

    personality = personality_map.get(companion_id, "linzixi")

    # 从事件脚本内容中获取图片配置
    script_content = event.script_content
    if isinstance(script_content, dict):
        image_config = script_content.get("image")
        if image_config:
            return f"/img/{personality}/{image_config}"

    # 如果没有特定图片配置，根据等级返回默认图片
    level_image_map = {
        "acquaintance": "C1-0.jpg",
        "friend": "C2-0.jpg",
        "close_friend": "C3-0.jpg",
        "special": "C4-0.jpg",
        "romantic": "C5-0.jpg"
    }

    trigger_conditions = event.trigger_conditions
    if isinstance(trigger_conditions, dict):
        level = trigger_conditions.get("level")
        if level and level in level_image_map:
            return f"/img/{personality}/{level_image_map[level]}"

    return None
