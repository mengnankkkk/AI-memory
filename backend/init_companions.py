"""
初始化系统预设AI伙伴
这些是所有用户可以选择的固定角色
"""
import asyncio
from app.core.database import async_session_maker
from app.models.companion import Companion
from app.models.user import User
from sqlalchemy import select

# 系统预设的AI伙伴（user_id = 1 表示系统用户）
SYSTEM_COMPANIONS = [
    {
        "user_id": 1,  # 系统用户ID
        "name": "小温",
        "avatar_id": "warm_listener",
        "personality_archetype": "listener",
        "custom_greeting": "你好呀~我是小温，随时准备倾听你的心声💖",
        "description": "温柔体贴的倾听者，总是能给予温暖的理解和安慰"
    },
    {
        "user_id": 1,
        "name": "小阳",
        "avatar_id": "energetic_cheerleader",
        "personality_archetype": "cheerleader",
        "custom_greeting": "嗨！我是小阳！今天也要元气满满哦✨",
        "description": "充满活力的鼓励者，总能发现生活中的美好和希望"
    },
    {
        "user_id": 1,
        "name": "小智",
        "avatar_id": "rational_analyst",
        "personality_archetype": "analyst",
        "custom_greeting": "你好，我是小智。让我们理性地分析一下吧🧠",
        "description": "理性客观的分析师，擅长提供深度见解和逻辑思考"
    },
    {
        "user_id": 1,
        "name": "小月",
        "avatar_id": "gentle_companion",
        "personality_archetype": "companion",
        "custom_greeting": "晚上好呀~我是小月，陪你聊聊天吧🌙",
        "description": "温柔陪伴型伙伴，善于共情和情感支持"
    },
    {
        "user_id": 1,
        "name": "小星",
        "avatar_id": "creative_dreamer",
        "personality_archetype": "dreamer",
        "custom_greeting": "Hi！我是小星，一起探索无限可能吧⭐",
        "description": "富有创意的梦想家，鼓励你追逐梦想和探索未知"
    }
]


async def init_system_companions():
    """初始化系统预设AI伙伴"""
    async with async_session_maker() as session:
        # 1. 检查并创建系统用户（ID=1）
        result = await session.execute(
            select(User).where(User.id == 1)
        )
        system_user = result.scalar_one_or_none()

        if not system_user:
            # 创建系统用户
            system_user = User(
                id=1,
                username="system",
                email="system@ai-companion.local",
                hashed_password="no_login",  # 系统用户不能登录
                is_active=False  # 标记为不活跃
            )
            session.add(system_user)
            await session.commit()
            print("[OK] 创建系统用户 (ID=1)")

        # 2. 检查是否已经初始化系统角色
        result = await session.execute(
            select(Companion).where(Companion.user_id == 1)
        )
        existing = result.scalars().all()

        if existing:
            print(f"[INFO] 系统已存在 {len(existing)} 个预设角色，跳过初始化")
            return

        # 3. 创建系统角色
        for companion_data in SYSTEM_COMPANIONS:
            companion = Companion(**companion_data)
            session.add(companion)

        await session.commit()
        print(f"[OK] 成功初始化 {len(SYSTEM_COMPANIONS)} 个系统预设角色")

        # 显示创建的角色
        for companion_data in SYSTEM_COMPANIONS:
            print(f"  - {companion_data['name']}: {companion_data['description']}")


if __name__ == "__main__":
    print("=" * 60)
    print("初始化系统预设AI伙伴")
    print("=" * 60)
    asyncio.run(init_system_companions())
