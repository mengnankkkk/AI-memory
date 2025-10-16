# -*- coding: utf-8 -*-
"""
事件系统初始化数据
定义所有主线事件和随机事件
"""
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import async_session_maker
from app.models.event import Event
import logging

logger = logging.getLogger("event_seed")


# 主线事件配置 - 等级提升事件
MAIN_EVENTS = [
    {
        "event_code": "LEVEL_UP_ACQUAINTANCE",
        "event_name": "破冰时刻",
        "event_type": "MAIN",
        "category": "milestone",
        "trigger_conditions": {"level": "acquaintance"},
        "is_repeatable": False,
        "cooldown_hours": 0,
        "script_content": {
            "title": "破冰时刻",
            "description": "你们的关系有了初步的进展",
            "dialogue": [
                {"speaker": "system", "text": "随着交流的深入，{name}对你的态度变得更加自然了..."},
                {"speaker": "companion", "text": "嗯...感觉和你聊天还挺舒服的。"}
            ]
        },
        "effects": {"trust": 5},
        "priority": 100,
        "is_active": True,
        "description": '当关系达到"认识"阶段时触发'
    },
    {
        "event_code": "LEVEL_UP_FRIEND",
        "event_name": "友谊确认",
        "event_type": "MAIN",
        "category": "milestone",
        "trigger_conditions": {"level": "friend"},
        "is_repeatable": False,
        "cooldown_hours": 0,
        "script_content": {
            "title": "友谊确认",
            "description": "你们成为了真正的朋友",
            "dialogue": [
                {"speaker": "system", "text": "{name}露出了真诚的笑容..."},
                {"speaker": "companion", "text": "我觉得...我们已经是朋友了吧？"}
            ]
        },
        "effects": {"trust": 10, "tension": -5},
        "priority": 100,
        "is_active": True,
        "description": '当关系达到"朋友"阶段时触发'
    },
    {
        "event_code": "LEVEL_UP_CLOSE_FRIEND",
        "event_name": "深度连结",
        "event_type": "MAIN",
        "category": "milestone",
        "trigger_conditions": {"level": "close_friend"},
        "is_repeatable": False,
        "cooldown_hours": 0,
        "script_content": {
            "title": "深度连结",
            "description": "你们的友谊进入了全新的层次",
            "dialogue": [
                {"speaker": "system", "text": "{name}的眼神中充满了信任..."},
                {"speaker": "companion", "text": "能认识你，真的很幸运。"}
            ]
        },
        "effects": {"trust": 15},
        "priority": 100,
        "is_active": True,
        "description": '当关系达到"好友"阶段时触发'
    },
    {
        "event_code": "LEVEL_UP_SPECIAL",
        "event_name": "特殊存在",
        "event_type": "MAIN",
        "category": "milestone",
        "trigger_conditions": {"level": "special"},
        "is_repeatable": False,
        "cooldown_hours": 0,
        "script_content": {
            "title": "特殊存在",
            "description": "你在{name}心中变得特别起来...",
            "dialogue": [
                {"speaker": "system", "text": "{name}的脸颊微微泛红..."},
                {"speaker": "companion", "text": "说实话...你对我来说，变得很特别了。"}
            ]
        },
        "effects": {"trust": 20},
        "priority": 100,
        "is_active": True,
        "description": '当关系达到"特别的人"阶段时触发'
    },
    {
        "event_code": "LEVEL_UP_ROMANTIC",
        "event_name": "心动时刻",
        "event_type": "MAIN",
        "category": "romance",
        "trigger_conditions": {"level": "romantic"},
        "is_repeatable": False,
        "cooldown_hours": 0,
        "script_content": {
            "title": "心动时刻",
            "description": "暧昧的气氛在你们之间蔓延...",
            "dialogue": [
                {"speaker": "system", "text": "{name}低下头，声音变得轻柔..."},
                {"speaker": "companion", "text": "我...好像对你有了不一样的感觉..."}
            ]
        },
        "effects": {"trust": 25},
        "priority": 100,
        "is_active": True,
        "description": '当关系达到"心动"阶段时触发'
    },
    {
        "event_code": "LEVEL_UP_LOVER",
        "event_name": "表白时刻",
        "event_type": "MAIN",
        "category": "romance",
        "trigger_conditions": {"level": "lover"},
        "is_repeatable": False,
        "cooldown_hours": 0,
        "script_content": {
            "title": "表白时刻",
            "description": "这是决定你们关系的重要时刻",
            "dialogue": [
                {"speaker": "system", "text": "{name}深吸一口气，鼓起勇气看着你..."},
                {"speaker": "companion", "text": "我想...我们可以在一起了吧？"}
            ]
        },
        "effects": {"trust": 30},
        "priority": 100,
        "is_active": True,
        "description": '当关系达到"恋人"阶段时触发'
    }
]


# 随机事件配置
RANDOM_EVENTS = [
    {
        "event_code": "RANDOM_CAFE_MEETING",
        "event_name": "咖啡馆的偶遇",
        "event_type": "RANDOM",
        "category": "daily",
        "trigger_conditions": {
            "min_affinity": 250,
            "max_affinity": 600
        },
        "is_repeatable": True,
        "cooldown_hours": 168,  # 1周冷却
        "script_content": {
            "title": "咖啡馆的偶遇",
            "description": "今天在咖啡馆遇到了{name}...",
            "dialogue": [
                {"speaker": "system", "text": "你在咖啡馆点单时，突然听到熟悉的声音..."},
                {"speaker": "companion", "text": "诶？这么巧，你也在这里？"}
            ]
        },
        "effects": {"affinity": 5, "trust": 2},
        "priority": 50,
        "is_active": True,
        "description": "在友谊阶段随机触发的日常偶遇事件"
    },
    {
        "event_code": "RANDOM_LATE_NIGHT_CHAT",
        "event_name": "深夜的交心",
        "event_type": "RANDOM",
        "category": "daily",
        "trigger_conditions": {
            "min_affinity": 450,
            "max_affinity": 750
        },
        "is_repeatable": True,
        "cooldown_hours": 240,  # 10天冷却
        "script_content": {
            "title": "深夜的交心",
            "description": "深夜时分，{name}向你敞开了心扉...",
            "dialogue": [
                {"speaker": "system", "text": "已经很晚了，但{name}似乎还想和你聊聊..."},
                {"speaker": "companion", "text": "你知道吗...今天遇到的事情让我想了很多..."}
            ]
        },
        "effects": {"affinity": 10, "trust": 5},
        "priority": 60,
        "is_active": True,
        "description": "在深度关系阶段随机触发的深夜对话事件"
    },
    {
        "event_code": "RANDOM_GIFT_EXCHANGE",
        "event_name": "意外的礼物",
        "event_type": "RANDOM",
        "category": "daily",
        "trigger_conditions": {
            "min_affinity": 350,
            "max_affinity": 800
        },
        "is_repeatable": True,
        "cooldown_hours": 336,  # 2周冷却
        "script_content": {
            "title": "意外的礼物",
            "description": "{name}送给你一份小礼物...",
            "dialogue": [
                {"speaker": "system", "text": "{name}从包里拿出一个小盒子，有些不好意思地递给你..."},
                {"speaker": "companion", "text": "这个...前几天看到觉得很适合你，就买下来了。"}
            ]
        },
        "effects": {"affinity": 8, "trust": 3},
        "priority": 55,
        "is_active": True,
        "description": "在友好关系阶段随机触发的礼物赠送事件"
    },
    {
        "event_code": "RANDOM_MOVIE_DATE",
        "event_name": "电影约会",
        "event_type": "RANDOM",
        "category": "daily",
        "trigger_conditions": {
            "min_affinity": 600,
            "max_affinity": 900
        },
        "is_repeatable": True,
        "cooldown_hours": 168,
        "script_content": {
            "title": "电影约会",
            "description": "{name}邀请你一起去看电影...",
            "dialogue": [
                {"speaker": "system", "text": "{name}似乎鼓起勇气想说些什么..."},
                {"speaker": "companion", "text": "那个...最近有部电影我很想看，要不要一起去？"}
            ]
        },
        "effects": {"affinity": 12, "trust": 5},
        "priority": 70,
        "is_active": True,
        "description": "在特殊关系阶段随机触发的约会事件"
    }
]


async def seed_events():
    """初始化事件数据"""
    try:
        async with async_session_maker() as session:
            created_count = 0
            updated_count = 0

            # 插入主线事件
            for event_data in MAIN_EVENTS:
                stmt = select(Event).where(Event.event_code == event_data["event_code"])
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()

                if not existing:
                    event = Event(**event_data)
                    session.add(event)
                    created_count += 1
                    logger.info(f"创建主线事件: {event_data['event_name']}")
                else:
                    # 更新现有事件
                    for key, value in event_data.items():
                        setattr(existing, key, value)
                    updated_count += 1
                    logger.info(f"更新主线事件: {event_data['event_name']}")

            # 插入随机事件
            for event_data in RANDOM_EVENTS:
                stmt = select(Event).where(Event.event_code == event_data["event_code"])
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()

                if not existing:
                    event = Event(**event_data)
                    session.add(event)
                    created_count += 1
                    logger.info(f"创建随机事件: {event_data['event_name']}")
                else:
                    # 更新现有事件
                    for key, value in event_data.items():
                        setattr(existing, key, value)
                    updated_count += 1
                    logger.info(f"更新随机事件: {event_data['event_name']}")

            await session.commit()
            logger.info(f"事件数据初始化完成: 创建 {created_count} 个，更新 {updated_count} 个")
            return created_count, updated_count

    except SQLAlchemyError as e:
        logger.error(f"事件数据初始化失败: {e}", exc_info=True)
        raise
