"""
初始化事件系统数据
运行此脚本以创建事件表并导入初始事件数据
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import init_db
from app.core.event_seed import seed_events


async def main():
    """主函数"""
    print("=" * 60)
    print("事件系统初始化脚本")
    print("=" * 60)
    print()

    # 1. 初始化数据库
    print("[1/2] 初始化数据库连接...")
    try:
        await init_db()
        print("[成功] 数据库连接成功")
    except Exception as e:
        print(f"[失败] 数据库连接失败: {e}")
        return

    # 2. 导入事件数据
    print("\n[2/2] 导入事件数据...")
    try:
        created_count, updated_count = await seed_events()
        print(f"[成功] 事件数据导入完成:")
        print(f"   - 新创建: {created_count} 个")
        print(f"   - 更新: {updated_count} 个")
    except Exception as e:
        print(f"[失败] 导入事件数据失败: {e}")
        import traceback
        traceback.print_exc()
        return

    print()
    print("=" * 60)
    print("[完成] 事件系统初始化完成！")
    print("=" * 60)
    print()
    print("你现在可以：")
    print("1. 启动后端服务: uvicorn app.main:socket_app --reload --port 8000")
    print("2. 启动前端服务: cd frontend && npm run dev")
    print("3. 聊天时好感度提升会自动触发事件")
    print()


if __name__ == "__main__":
    asyncio.run(main())
