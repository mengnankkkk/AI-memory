"""
重新初始化数据库
"""
import asyncio
from app.core.database import engine, Base, init_db
from app.models.companion import Companion, Message
from app.models.chat_session import ChatSession, ChatMessage

async def recreate_database():
    """重新创建数据库"""
    print("=" * 60)
    print("  Recreating Database with All Tables")
    print("=" * 60)

    # 删除所有表
    print("[INFO] Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("[OK] All tables dropped")

    # 创建所有表
    print("[INFO] Creating all tables...")
    await init_db()
    print("[OK] All tables created")

    # 验证表结构
    print("\n[INFO] Verifying table structure...")
    from sqlalchemy import text
    async with engine.begin() as conn:
        # 检查 companions 表
        result = await conn.execute(text("PRAGMA table_info(companions)"))
        columns = result.fetchall()
        print(f"\n[companions] table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

        # 检查其他表
        for table_name in ['messages', 'chat_sessions', 'chat_messages']:
            result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
            columns = result.fetchall()
            print(f"\n[{table_name}] table columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")

    print("\n" + "=" * 60)
    print("[OK] Database recreated successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(recreate_database())
