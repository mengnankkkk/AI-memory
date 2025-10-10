"""Database seeding utilities for ensuring baseline data exists."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import async_session_maker
from app.models.user import User
from app.models.companion import Companion
from app.models.relationship import CompanionRelationshipState

logger = logging.getLogger("database_seed")


SYSTEM_COMPANIONS: List[Dict] = [
    {
        "id": 1,
        "user_id": 1,
        "name": "林梓汐",
        "avatar_id": "linzixi",
        "personality_archetype": "linzixi",
        "custom_greeting": "权限验证完成。我是林梓汐博士，普罗米修斯计划总监。你的访问请求已被记录。有什么需要我协助分析的吗？",
        "description": "逻辑控制的天才博士",
        "prompt_version": "v1",
    },
    {
        "id": 2,
        "user_id": 1,
        "name": "雪见",
        "avatar_id": "xuejian",
        "personality_archetype": "xuejian",
        "custom_greeting": "检测到新的连接请求。我是雪见，系统安全主管。你的权限等级：临时访问。有什么问题？",
        "description": "网络安全专家",
        "prompt_version": "v1",
    },
    {
        "id": 3,
        "user_id": 1,
        "name": "凪",
        "avatar_id": "nagi",
        "personality_archetype": "nagi",
        "custom_greeting": "哈喽！我是凪~今天也要画出最棒的作品！有什么想聊的吗？",
        "description": "VTuber偶像画师",
        "prompt_version": "v1",
    },
    {
        "id": 4,
        "user_id": 1,
        "name": "时雨",
        "avatar_id": "shiyu",
        "personality_archetype": "shiyu",
        "custom_greeting": "你好，我是时雨。在数字的尘埃中，我们又相遇了...有什么想要探讨的吗？",
        "description": "数字历史学家",
        "prompt_version": "v1",
    },
    {
        "id": 5,
        "user_id": 1,
        "name": "Zoe",
        "avatar_id": "zoe",
        "personality_archetype": "zoe",
        "custom_greeting": "Hey！我是Zoe，欢迎来到我的领域。准备好接受挑战了吗？😎",
        "description": "硅谷颠覆者CEO",
        "prompt_version": "v1",
    },
    {
        "id": 6,
        "user_id": 1,
        "name": "凯文",
        "avatar_id": "kevin",
        "personality_archetype": "kevin",
        "custom_greeting": "哟！兄弟，我是凯文！_(:з」∠)_ 今天又有什么破事要吐槽吗？",
        "description": "技术宅朋友",
        "prompt_version": "v1",
    },
]


DEFAULT_RELATIONSHIP_STATE: Dict[str, object] = {
    "affinity_score": 50,
    "trust_score": 10,
    "tension_score": 0,
    "romance_stage": "stranger",
    "current_mood": "neutral",
    "total_interactions": 0,
    "positive_interactions": 0,
    "negative_interactions": 0,
}


async def seed_initial_data() -> None:
    """Seed baseline data required for the application to function."""

    await _ensure_system_user()
    await _ensure_system_companions()
    await _ensure_relationship_states_for_existing_users()


async def _ensure_system_user() -> None:
    async with async_session_maker() as session:
        try:
            result = await session.execute(select(User).where(User.id == 1))
            system_user = result.scalar_one_or_none()

            if system_user:
                return

            system_user = User(
                id=1,
                username="system",
                email="system@ai-companion.local",
                hashed_password="no_login",
                is_active=False,
            )
            session.add(system_user)
            await session.commit()
            logger.info("Seeded system user (ID=1)")
        except SQLAlchemyError:
            await session.rollback()
            logger.exception("Failed to seed system user")
            raise


async def _ensure_system_companions() -> None:
    async with async_session_maker() as session:
        try:
            changed = False
            for companion_data in SYSTEM_COMPANIONS:
                result = await session.execute(
                    select(Companion).where(Companion.id == companion_data["id"])
                )
                companion = result.scalar_one_or_none()

                if companion:
                    # Ensure core fields stay in sync
                    updated = False
                    for field, value in companion_data.items():
                        if getattr(companion, field, None) != value:
                            setattr(companion, field, value)
                            updated = True
                    if updated:
                        changed = True
                else:
                    session.add(Companion(**companion_data))
                    changed = True

            if changed:
                await session.commit()
                logger.info("Seeded system companions")
        except SQLAlchemyError:
            await session.rollback()
            logger.exception("Failed to seed system companions")
            raise


async def _ensure_relationship_states_for_existing_users() -> None:
    async with async_session_maker() as session:
        try:
            users_result = await session.execute(
                select(User).where(User.id != 1)
            )
            users = users_result.scalars().all()

            if not users:
                return

            companions_result = await session.execute(
                select(Companion).where(Companion.user_id == 1)
            )
            system_companions = companions_result.scalars().all()

            if not system_companions:
                return

            now = datetime.now(timezone.utc)
            created_any = False

            for user in users:
                for companion in system_companions:
                    state_result = await session.execute(
                        select(CompanionRelationshipState).where(
                            CompanionRelationshipState.user_id == str(user.id),
                            CompanionRelationshipState.companion_id == str(companion.id),
                        )
                    )
                    existing_state = state_result.scalar_one_or_none()

                    if existing_state:
                        continue

                    state = CompanionRelationshipState(
                        user_id=str(user.id),
                        companion_id=str(companion.id),
                        affinity_score=DEFAULT_RELATIONSHIP_STATE["affinity_score"],
                        trust_score=DEFAULT_RELATIONSHIP_STATE["trust_score"],
                        tension_score=DEFAULT_RELATIONSHIP_STATE["tension_score"],
                        romance_stage=DEFAULT_RELATIONSHIP_STATE["romance_stage"],
                        current_mood=DEFAULT_RELATIONSHIP_STATE["current_mood"],
                        total_interactions=DEFAULT_RELATIONSHIP_STATE["total_interactions"],
                        positive_interactions=DEFAULT_RELATIONSHIP_STATE["positive_interactions"],
                        negative_interactions=DEFAULT_RELATIONSHIP_STATE["negative_interactions"],
                        special_flags={
                            "seeded": True,
                            "seeded_at": now.isoformat(),
                        },
                        last_interaction_at=now,
                    )
                    session.add(state)
                    created_any = True

            if created_any:
                await session.commit()
                logger.info("Seeded default relationship states for existing users")
        except SQLAlchemyError:
            await session.rollback()
            logger.exception("Failed to seed relationship states")
            raise
