"""
事件触发引擎
集成到AffinityEngine中，当好感度等级变化时自动触发事件
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import SQLAlchemyError
import random
import logging

from app.core.database import async_session_maker
from app.models.event import Event, UserEventHistory
from app.models.relationship import CompanionRelationshipState

logger = logging.getLogger("event_engine")


class EventEngine:
    """事件触发引擎"""

    # 等级到图片编号映射
    LEVEL_TO_IMAGE_MAP = {
        "stranger": None,           # 无图片事件
        "acquaintance": "C1",       # 破冰
        "friend": "C2",             # 友情
        "close_friend": "C3",       # 深度交流
        "special": "C4",            # 特殊关系
        "romantic": "C5",           # 心动时刻
        "lover": None               # 恋人专属（需要自定义）
    }

    # 角色ID映射
    PERSONALITY_MAP = {
        1: "linzixi",
        2: "xuejian",
        3: "nagi",
        4: "shiyu",
        5: "zoe",
        6: "kevin"
    }

    async def check_and_trigger_events(
        self,
        user_id: str,
        companion_id: int,
        companion_name: str,
        old_level: str,
        new_level: str,
        new_affinity_score: int,
        level_up: bool
    ) -> List[Dict[str, Any]]:
        """
        检查并触发事件

        Returns:
            触发的事件列表
        """
        triggered_events = []

        try:
            # 1. 检查等级变化事件（主线事件）
            if level_up:
                level_event = await self._trigger_level_up_event(
                    user_id, companion_id, companion_name, new_level
                )
                if level_event:
                    triggered_events.append(level_event)
                    logger.info(f"[EventEngine] 触发等级事件: {level_event['event_name']}")

            # 2. 检查随机事件（基于当前关系状态）
            random_event = await self._check_random_event(
                user_id, companion_id, companion_name, new_level, new_affinity_score
            )
            if random_event:
                triggered_events.append(random_event)
                logger.info(f"[EventEngine] 触发随机事件: {random_event['event_name']}")

            # 3. 检查特殊日期事件
            date_event = await self._check_date_event(
                user_id, companion_id, companion_name
            )
            if date_event:
                triggered_events.append(date_event)
                logger.info(f"[EventEngine] 触发日期事件: {date_event['event_name']}")

            return triggered_events

        except Exception as e:
            logger.error(f"[EventEngine] 检查事件失败: {e}", exc_info=True)
            return []

    async def _trigger_level_up_event(
        self,
        user_id: str,
        companion_id: int,
        companion_name: str,
        new_level: str
    ) -> Optional[Dict[str, Any]]:
        """触发等级提升主线事件"""
        try:
            async with async_session_maker() as session:
                # 查找对应等级的主线事件
                stmt = select(Event).where(
                    and_(
                        Event.event_type == "MAIN",
                        Event.is_active == True
                    )
                )
                result = await session.execute(stmt)
                events = result.scalars().all()

                # 筛选匹配等级的事件
                matched_event = None
                for event in events:
                    trigger_level = event.trigger_conditions.get("level")
                    if trigger_level == new_level:
                        matched_event = event
                        break

                if not matched_event:
                    logger.warning(f"未找到等级 {new_level} 的主线事件")
                    return None

                # 检查是否已触发过
                history_stmt = select(UserEventHistory).where(
                    and_(
                        UserEventHistory.user_id == user_id,
                        UserEventHistory.companion_id == str(companion_id),
                        UserEventHistory.event_id == matched_event.event_id,
                        UserEventHistory.is_completed == True
                    )
                )
                history_result = await session.execute(history_stmt)
                existing_history = history_result.scalar_one_or_none()

                if existing_history and not matched_event.is_repeatable:
                    logger.info(f"事件 {matched_event.event_code} 已触发过且不可重复")
                    return None

                # 创建事件历史记录
                history = UserEventHistory(
                    user_id=user_id,
                    companion_id=str(companion_id),
                    event_id=matched_event.event_id,
                    event_code=matched_event.event_code,
                    is_completed=False,
                    triggered_at=datetime.now(timezone.utc)
                )
                session.add(history)
                await session.commit()
                await session.refresh(history)

                # 构建事件数据
                image_code = self.LEVEL_TO_IMAGE_MAP.get(new_level)
                image_url = None
                if image_code:
                    # 根据角色和等级获取图片
                    personality = self.PERSONALITY_MAP.get(companion_id, "linzixi")
                    image_url = f"/img/{personality}/{image_code}-0.jpg"

                return {
                    "event_id": matched_event.event_id,
                    "event_code": matched_event.event_code,
                    "event_name": matched_event.event_name,
                    "event_type": matched_event.event_type,
                    "category": matched_event.category,
                    "script_content": matched_event.script_content,
                    "image_url": image_url,
                    "history_id": history.id,
                    "companion_name": companion_name,
                    "triggered_at": history.triggered_at.isoformat()
                }

        except Exception as e:
            logger.error(f"[EventEngine] 触发等级事件失败: {e}", exc_info=True)
            return None

    async def _check_random_event(
        self,
        user_id: str,
        companion_id: int,
        companion_name: str,
        current_level: str,
        affinity_score: int
    ) -> Optional[Dict[str, Any]]:
        """检查随机事件（概率触发）"""
        # 随机事件触发概率：5%
        if random.random() > 0.05:
            return None

        try:
            async with async_session_maker() as session:
                # 查找适合当前等级的随机事件
                stmt = select(Event).where(
                    and_(
                        Event.event_type == "RANDOM",
                        Event.is_active == True
                    )
                )
                result = await session.execute(stmt)
                events = result.scalars().all()

                # 筛选符合条件的事件
                eligible_events = []
                for event in events:
                    conditions = event.trigger_conditions
                    min_affinity = conditions.get("min_affinity", 0)
                    max_affinity = conditions.get("max_affinity", 1000)

                    if min_affinity <= affinity_score <= max_affinity:
                        # 检查冷却时间
                        if await self._check_cooldown(user_id, companion_id, event, session):
                            eligible_events.append(event)

                if not eligible_events:
                    return None

                # 随机选择一个事件
                selected_event = random.choice(eligible_events)

                # 创建历史记录
                history = UserEventHistory(
                    user_id=user_id,
                    companion_id=str(companion_id),
                    event_id=selected_event.event_id,
                    event_code=selected_event.event_code,
                    is_completed=False,
                    triggered_at=datetime.now(timezone.utc)
                )
                session.add(history)
                await session.commit()
                await session.refresh(history)

                # 获取随机事件图片
                image_url = self._get_random_event_image(companion_id)

                return {
                    "event_id": selected_event.event_id,
                    "event_code": selected_event.event_code,
                    "event_name": selected_event.event_name,
                    "event_type": selected_event.event_type,
                    "category": selected_event.category,
                    "script_content": selected_event.script_content,
                    "image_url": image_url,
                    "history_id": history.id,
                    "companion_name": companion_name,
                    "triggered_at": history.triggered_at.isoformat()
                }

        except Exception as e:
            logger.error(f"[EventEngine] 检查随机事件失败: {e}", exc_info=True)
            return None

    async def _check_date_event(
        self,
        user_id: str,
        companion_id: int,
        companion_name: str
    ) -> Optional[Dict[str, Any]]:
        """检查特殊日期事件（节日、纪念日等）"""
        # TODO: 实现日期事件检查逻辑
        return None

    async def _check_cooldown(
        self,
        user_id: str,
        companion_id: int,
        event: Event,
        session
    ) -> bool:
        """检查事件冷却时间"""
        if event.cooldown_hours == 0:
            return True

        try:
            stmt = select(UserEventHistory).where(
                and_(
                    UserEventHistory.user_id == user_id,
                    UserEventHistory.companion_id == str(companion_id),
                    UserEventHistory.event_id == event.event_id
                )
            ).order_by(UserEventHistory.triggered_at.desc())

            result = await session.execute(stmt)
            last_trigger = result.scalar_one_or_none()

            if not last_trigger:
                return True

            cooldown_end = last_trigger.triggered_at + timedelta(hours=event.cooldown_hours)
            return datetime.now(timezone.utc) >= cooldown_end

        except Exception as e:
            logger.error(f"[EventEngine] 检查冷却时间失败: {e}")
            return False

    def _get_random_event_image(self, companion_id: int) -> Optional[str]:
        """获取随机事件图片"""
        personality = self.PERSONALITY_MAP.get(companion_id, "linzixi")
        # 随机选择一张图片
        image_codes = ["C1", "C2", "C3", "C4", "C5"]
        selected_code = random.choice(image_codes)
        variant = random.choice([0, 1])
        return f"/img/{personality}/{selected_code}-{variant}.jpg"


# 全局实例
event_engine = EventEngine()
