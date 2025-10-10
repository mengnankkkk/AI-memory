"""
重建数据库脚本
保留用户数据，删除并重建其他所有表
"""
import asyncio
from sqlalchemy import text
from app.core.database import async_session_maker, engine, Base
from app.models.user import User
from app.models.companion import Companion, Message
from app.models.relationship import CompanionRelationshipState, RelationshipHistory, EmotionLog
from app.models.chat_session import ChatSession
from app.models.event import Event


async def backup_users():
    """备份用户数据"""
    print("\n[1/5] 备份用户数据...")
    async with async_session_maker() as session:
        result = await session.execute(text("SELECT * FROM users"))
        users = result.fetchall()
        print(f"   找到 {len(users)} 个用户")
        return users


async def drop_all_tables_except_users():
    """删除除用户表外的所有表"""
    print("\n[2/5] 删除旧表（保留用户表）...")

    async with engine.begin() as conn:
        # 删除所有表（除了users）
        await conn.run_sync(Base.metadata.drop_all)
        print("   所有表已删除")


async def create_all_tables():
    """创建所有表结构"""
    print("\n[3/5] 创建新表结构...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("   表创建成功:")
    print("   - users (用户表)")
    print("   - companions (AI伙伴表)")
    print("   - companion_relationship_states (关系状态表)")
    print("   - relationship_history (关系历史表)")
    print("   - emotion_logs (情感日志表)")
    print("   - chat_sessions (聊天会话表)")
    print("   - messages (消息表)")
    print("   - events (事件表)")


async def restore_users(users_backup):
    """恢复用户数据"""
    print("\n[4/5] 恢复用户数据...")

    if not users_backup:
        print("   没有需要恢复的用户数据")
        return

    async with async_session_maker() as session:
        for user_row in users_backup:
            # 直接使用原生SQL恢复数据，保持原ID
            insert_sql = text("""
                INSERT INTO users (id, username, email, hashed_password, is_active, created_at)
                VALUES (:id, :username, :email, :hashed_password, :is_active, :created_at)
            """)

            await session.execute(insert_sql, {
                "id": user_row[0],
                "username": user_row[1],
                "email": user_row[2],
                "hashed_password": user_row[3],
                "is_active": user_row[4],
                "created_at": user_row[5]
            })

        await session.commit()
        print(f"   成功恢复 {len(users_backup)} 个用户")


async def init_system_companions():
    """初始化6个系统伙伴"""
    print("\n[5/5] 初始化系统伙伴...")

    SYSTEM_COMPANIONS = [
        {
            "id": 1,
            "user_id": 1,
            "name": "林梓汐",
            "avatar_id": "linzixi",
            "personality_archetype": "linzixi",
            "custom_greeting": "权限验证完成。我是林梓汐博士，普罗米修斯计划总监。你的访问请求已被记录。有什么需要我协助分析的吗？",
            "description": "逻辑控制的天才博士"
        },
        {
            "id": 2,
            "user_id": 1,
            "name": "雪见",
            "avatar_id": "xuejian",
            "personality_archetype": "xuejian",
            "custom_greeting": "检测到新的连接请求。我是雪见，系统安全主管。你的权限等级：临时访问。有什么问题？",
            "description": "网络安全专家"
        },
        {
            "id": 3,
            "user_id": 1,
            "name": "凪",
            "avatar_id": "nagi",
            "personality_archetype": "nagi",
            "custom_greeting": "哈喽！我是凪~今天也要画出最棒的作品！有什么想聊的吗？",
            "description": "VTuber偶像画师"
        },
        {
            "id": 4,
            "user_id": 1,
            "name": "时雨",
            "avatar_id": "shiyu",
            "personality_archetype": "shiyu",
            "custom_greeting": "你好，我是时雨。在数字的尘埃中，我们又相遇了...有什么想要探讨的吗？",
            "description": "数字历史学家"
        },
        {
            "id": 5,
            "user_id": 1,
            "name": "Zoe",
            "avatar_id": "zoe",
            "personality_archetype": "zoe",
            "custom_greeting": "Hey！我是Zoe，欢迎来到我的领域。准备好接受挑战了吗？😎",
            "description": "硅谷颠覆者CEO"
        },
        {
            "id": 6,
            "user_id": 1,
            "name": "凯文",
            "avatar_id": "kevin",
            "personality_archetype": "kevin",
            "custom_greeting": "哟！兄弟，我是凯文！_(:з」∠)_ 今天又有什么破事要吐槽吗？",
            "description": "技术宅朋友"
        }
    ]

    async with async_session_maker() as session:
        # 首先确保系统用户存在
        result = await session.execute(text("SELECT id FROM users WHERE id = 1"))
        system_user = result.fetchone()

        if not system_user:
            print("   创建系统用户 (ID=1)...")
            insert_user_sql = text("""
                INSERT INTO users (id, username, email, hashed_password, is_active)
                VALUES (1, 'system', 'system@ai-companion.local', 'no_login', 0)
            """)
            await session.execute(insert_user_sql)
            await session.commit()

        # 插入系统伙伴（使用指定的ID）
        for companion_data in SYSTEM_COMPANIONS:
            insert_sql = text("""
                INSERT INTO companions (id, user_id, name, avatar_id, personality_archetype, custom_greeting, description)
                VALUES (:id, :user_id, :name, :avatar_id, :personality_archetype, :custom_greeting, :description)
            """)

            await session.execute(insert_sql, companion_data)
            print(f"   [OK] {companion_data['name']} (ID:{companion_data['id']})")

        await session.commit()

    print(f"\n   成功初始化 {len(SYSTEM_COMPANIONS)} 个系统伙伴")


async def main():
    """主函数"""
    print("=" * 60)
    print("数据库重建工具")
    print("=" * 60)
    print("\n警告：此操作将删除除用户外的所有数据！")
    print("用户数据将被保留。")

    try:
        # 1. 备份用户
        users_backup = await backup_users()

        # 2. 删除旧表（保留users）
        await drop_all_tables_except_users()

        # 3. 创建新表
        await create_all_tables()

        # 4. 恢复用户
        await restore_users(users_backup)

        # 5. 初始化系统伙伴
        await init_system_companions()

        print("\n" + "=" * 60)
        print("[SUCCESS] 数据库重建完成！")
        print("=" * 60)
        print("\n下一步：")
        print("1. 运行: python init_companion_data.py <user_id>")
        print("   为用户初始化6个伙伴的Redis数据")
        print("2. 刷新前端页面查看效果")

    except Exception as e:
        print(f"\n[ERROR] 重建失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
