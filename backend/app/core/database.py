from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# 创建异步引擎
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# 为了兼容性，保留原名称
engine = async_engine

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 声明基类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库"""
    from app.core.seed import seed_initial_data

    # 导入所有模型以确保它们被注册
    from app.models.user import User
    from app.models.companion import Companion, Message
    from app.models.chat_session import ChatSession, ChatMessage
    from app.models.relationship import (
        CompanionRelationshipState,
        RelationshipHistory,
        EmotionLog
    )
    from app.models.event import (
        Event,
        UserEventHistory,
        OfflineLifeLog,
        EventTemplate
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_initial_data()
