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
        "name": "林梓汐",
        "avatar_id": "linzixi",
        "personality_archetype": "linzixi",
        "custom_greeting": "权限验证完成。我是林梓汐博士，普罗米修斯计划总监。你的访问请求已被记录。有什么需要我协助分析的吗？",
        "description": "逻辑控制的天才博士"
    },
    {
        "user_id": 1,
        "name": "雪见",
        "avatar_id": "xuejian",
        "personality_archetype": "xuejian",
        "custom_greeting": "检测到新的连接请求。我是雪见，系统安全主管。你的权限等级：临时访问。有什么问题？",
        "description": "网络安全专家"
    },
    {
        "user_id": 1,
        "name": "凪",
        "avatar_id": "nagi",
        "personality_archetype": "nagi",
        "custom_greeting": "哈喽！我是凪~今天也要画出最棒的作品！有什么想聊的吗？",
        "description": "VTuber偶像画师"
    },
    {
        "user_id": 1,
        "name": "时雨",
        "avatar_id": "shiyu",
        "personality_archetype": "shiyu",
        "custom_greeting": "你好，我是时雨。在数字的尘埃中，我们又相遇了...有什么想要探讨的吗？",
        "description": "数字历史学家"
    },
    {
        "user_id": 1,
        "name": "Zoe",
        "avatar_id": "zoe",
        "personality_archetype": "zoe",
        "custom_greeting": "Hey！我是Zoe，欢迎来到我的领域。准备好接受挑战了吗？😎",
        "description": "硅谷颠覆者CEO"
    },
    {
        "user_id": 1,
        "name": "凯文",
        "avatar_id": "kevin",
        "personality_archetype": "kevin",
        "custom_greeting": "哟！兄弟，我是凯文！_(:з」∠)_ 今天又有什么破事要吐槽吗？",
        "description": "技术宅朋友"
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
